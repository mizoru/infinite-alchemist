import os
import json
import re
import redis
import logging
import traceback
from functools import lru_cache
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain.llms import OpenAI, HuggingFaceEndpoint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        # Determine which LLM provider to use
        llm_provider = os.getenv("LLM_PROVIDER", "huggingface").lower()
        
        if llm_provider == "openai":
            # Initialize OpenAI LLM
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            self.llm = OpenAI(
                temperature=0.7,
                openai_api_key=api_key,
                model_name="gpt-4o-mini"
            )
        elif llm_provider == "huggingface":
            # Initialize Hugging Face LLM
            api_key = os.getenv("LLM_API_KEY")
            model_name = os.getenv("LLM_MODEL", "lightblue/suzume-llama-3-8B-multilingual")
            
            if not api_key:
                raise ValueError("LLM_API_KEY environment variable is not set")
            
            self.llm = HuggingFaceEndpoint(
                endpoint_url=f"https://api-inference.huggingface.co/models/{model_name}",
                huggingfacehub_api_token=api_key,
                task="text-generation",
                model_kwargs={
                    "temperature": 0.5,
                    "max_new_tokens": 150,
                    "do_sample": True,
                }
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Define the prompt template for element combinations
        self.combination_template = self._get_prompt_template()
        
        # Initialize Redis cache if available
        redis_url = os.getenv("REDIS_URL")
        self.cache_enabled = redis_url is not None
        if self.cache_enabled:
            try:
                self.redis = redis.from_url(redis_url)
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Redis cache: {e}")
                self.cache_enabled = False
        
        # Load prompt service if available
        try:
            from app.services.prompt_service import PromptService
            self.prompt_service = PromptService()
            self.use_prompt_service = True
        except (ImportError, Exception) as e:
            logger.warning(f"Prompt service not available: {e}")
            self.use_prompt_service = False
    
    def _get_cache_key(self, element1: str, element2: str, lang: str = "en") -> str:
        """Generate a consistent cache key for element combinations"""
        # Sort elements alphabetically to ensure consistent keys regardless of order
        sorted_elements = sorted([element1.lower(), element2.lower()])
        return f"element_combination:{lang}:{sorted_elements[0]}:{sorted_elements[1]}"
    
    def _get_from_cache(self, element1: str, element2: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Try to get a cached result for the element combination"""
        if not self.cache_enabled:
            return None
            
        cache_key = self._get_cache_key(element1, element2, lang)
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            try:
                return json.loads(cached_result)
            except json.JSONDecodeError:
                return None
        return None
    
    def _save_to_cache(self, element1: str, element2: str, result: Dict[str, Any], lang: str = "en") -> None:
        """Save a result to the cache"""
        if not self.cache_enabled:
            return
            
        cache_key = self._get_cache_key(element1, element2, lang)
        self.redis.set(cache_key, json.dumps(result), ex=60*60*24*7)  # Cache for 1 week
    
    # Update the memory cache to include language
    @lru_cache(maxsize=1000)
    def _memory_cache(self, element1: str, element2: str, lang: str = "en", prompt_name: str = "default") -> str:
        """In-memory cache fallback when Redis is not available"""
        # Generate the prompt
        prompt = self._get_formatted_prompt(element1, element2, lang, prompt_name)
        # Get response from LLM
        return self._get_llm_response(prompt)
    
    def _get_formatted_prompt(self, element1: str, element2: str, lang: str = "en", prompt_name: str = "default") -> str:
        """Get a formatted prompt for element combination"""
        try:
            # Try to load language-specific prompts
            prompt_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", f"{lang}.json")
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                    if prompt_name in prompts:
                        return prompts[prompt_name].format(element1=element1, element2=element2)
            
            # Fallback to English if language not found
            if lang != "en":
                logger.warning(f"Prompt not found for language {lang}, falling back to English")
                return self._get_formatted_prompt(element1, element2, "en", prompt_name)
            
            # Fallback to default template if nothing else works
            return self.combination_template.format(element1=element1, element2=element2)
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return self.combination_template.format(element1=element1, element2=element2)
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM"""
        return self.llm(prompt)
    
    def _get_prompt_template(self):
        """Get the prompt template for combining elements."""
        return """You are the Infinite Alchemist, a game about combining elements to create new ones.

TASK:
Combine {element1} and {element2} to create a new element.

IMPORTANT RULES:
1. Elements can ONLY be combined if they have a logical relationship.
2. Physical elements (like Water, Fire, Earth) can be combined with other physical elements.
3. Abstract concepts (like Love, Democracy, Philosophy) CANNOT be combined with physical elements.
4. Elements from completely different domains with no connection CANNOT be combined.
5. Combinations that violate the laws of physics or common sense are NOT allowed.
6. If the combination is valid, return a JSON object with the new element's name and an appropriate emoji.
7. If the combination is invalid or nonsensical, return a JSON object indicating it's impossible with a brief explanation.

RESPONSE FORMAT:
For valid combinations:
```json
{{
"valid": true,
"result": "New Element Name",
"emoji": "🔥"
}}
```

For invalid combinations:
```json
{{
"valid": false,
}}
```

Now, combine {element1} and {element2}:"""
    
    def combine_elements(self, element1: str, element2: str, lang: str = "en", prompt_name: str = "default") -> Dict[str, Any]:
        """
        Use the LLM to determine the result of combining two elements.
        
        Args:
            element1: The name of the first element
            element2: The name of the second element
            lang: Language code for the prompt ("en" or "ru")
            prompt_name: Name of the prompt to use
            
        Returns:
            A dictionary containing the result element's name and emoji
        """
        # Try to get from cache first
        cached_result = self._get_from_cache(element1, element2, lang)
        if cached_result:
            logger.info(f"Cache hit for {element1} + {element2} ({lang})")
            return cached_result
        
        # If not in cache, use the LLM
        try:
            # Use in-memory cache or direct LLM call
            if self.cache_enabled:
                prompt = self._get_formatted_prompt(element1, element2, lang, prompt_name)
                response = self._get_llm_response(prompt)
            else:
                # Use the memory cache with language support
                response = self._memory_cache(element1, element2, lang, prompt_name)
            
            # Log the full LLM response for debugging
            logger.info(f"\n\n==== LLM RESPONSE FOR {element1} + {element2} ({lang}) ====")
            logger.info(f"PROMPT: {self._get_formatted_prompt(element1, element2, lang, prompt_name)}")
            logger.info(f"RESPONSE: {response}")
            logger.info("==== END LLM RESPONSE ====\n\n")
            
            # Try to parse the response as JSON
            try:
                # Clean up the response - remove any markdown code blocks or extra text
                cleaned_response = response
                if "```json" in response:
                    json_blocks = re.findall(r'```(?:json)?(.*?)```', response, re.DOTALL)
                    if json_blocks:
                        cleaned_response = json_blocks[0].strip()
                
                # Fix common JSON issues
                cleaned_response = re.sub(r'"emoji":\s*([^",}\s]+)', r'"emoji": "\1"', cleaned_response)
                
                # Log the cleaned response
                logger.info(f"CLEANED RESPONSE: {cleaned_response}")
                
                # Parse the JSON
                result = json.loads(cleaned_response)
                
                # Log the parsed result
                logger.info(f"PARSED RESULT: {result}")
                
                # Ensure required fields are present
                if "valid" in result and result["valid"] == False:
                    # This is a refusal response
                    if "reason" not in result:
                        result["reason"] = "Эта комбинация невозможна." if lang == "ru" else "This combination is not possible."
                    
                    # Save to cache
                    self._save_to_cache(element1, element2, result, lang)
                    return result
                
                # For valid combinations
                if "result" not in result:
                    raise ValueError("Response missing 'result' field")
                
                # Add default emoji if missing
                if "emoji" not in result:
                    result["emoji"] = "✨"
                
                # Save to cache
                self._save_to_cache(element1, element2, result, lang)
                    
                return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"ERROR PARSING JSON RESPONSE: {e}")
                logger.error(f"RAW RESPONSE: {response}")
                logger.error(f"CLEANED RESPONSE: {cleaned_response}")
                
                # If we can't parse the response, treat it as a refusal
                refusal = {
                    "valid": False,
                    "reason": "Не удалось обработать ответ модели." if lang == "ru" else "Failed to process model response."
                }
                
                # Save to cache
                self._save_to_cache(element1, element2, refusal, lang)
                
                return refusal
                
        except Exception as e:
            logger.error(f"ERROR IN LLM SERVICE: {e}")
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            refusal = {
                "valid": False,
                "reason": f"An error occurred: {str(e)}"
            }
            return refusal 