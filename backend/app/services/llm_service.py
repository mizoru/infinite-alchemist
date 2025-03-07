import os
import json
import re
import redis
from functools import lru_cache
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain.llms import OpenAI, HuggingFaceEndpoint

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
                print("Redis cache initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Redis cache: {e}")
                self.cache_enabled = False
        
        # Load prompt service if available
        try:
            from app.services.prompt_service import PromptService
            self.prompt_service = PromptService()
            self.use_prompt_service = True
        except (ImportError, Exception) as e:
            print(f"Prompt service not available: {e}")
            self.use_prompt_service = False
    
    def _get_cache_key(self, element1: str, element2: str) -> str:
        """Generate a consistent cache key for element combinations"""
        # Sort elements alphabetically to ensure consistent keys regardless of order
        sorted_elements = sorted([element1.lower(), element2.lower()])
        return f"element_combination:{sorted_elements[0]}:{sorted_elements[1]}"
    
    def _get_from_cache(self, element1: str, element2: str) -> Optional[Dict[str, Any]]:
        """Try to get a cached result for the element combination"""
        if not self.cache_enabled:
            return None
            
        cache_key = self._get_cache_key(element1, element2)
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            try:
                return json.loads(cached_result)
            except json.JSONDecodeError:
                return None
        return None
    
    def _save_to_cache(self, element1: str, element2: str, result: Dict[str, Any]) -> None:
        """Save a result to the cache"""
        if not self.cache_enabled:
            return
            
        cache_key = self._get_cache_key(element1, element2)
        self.redis.set(cache_key, json.dumps(result), ex=60*60*24*7)  # Cache for 1 week
    
    # Fallback in-memory cache using Python's lru_cache
    @lru_cache(maxsize=1000)
    def _memory_cache(self, element1: str, element2: str) -> str:
        """In-memory cache fallback when Redis is not available"""
        # Generate the prompt
        prompt = self._get_formatted_prompt(element1, element2)
        # Get response from LLM
        return self._get_llm_response(prompt)
    
    def _get_formatted_prompt(self, element1: str, element2: str, lang: str = "en", prompt_name: str = "default") -> str:
        """Get a formatted prompt for element combination"""
        if self.use_prompt_service:
            return self.prompt_service.format_prompt(lang, prompt_name, element1, element2)
        else:
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
            lang: Language code for the prompt
            prompt_name: Name of the prompt to use
            
        Returns:
            A dictionary containing the result element's name, emoji, and description
        """
        # Try to get from cache first
        cached_result = self._get_from_cache(element1, element2)
        if cached_result:
            print(f"Cache hit for {element1} + {element2}")
            return cached_result
        
        # If not in cache, use the LLM
        try:
            # Use in-memory cache or direct LLM call
            if self.cache_enabled:
                prompt = self._get_formatted_prompt(element1, element2, lang, prompt_name)
                response = self._get_llm_response(prompt)
            else:
                # Use the memory cache with default prompt
                response = self._memory_cache(element1, element2)
            
            # Try to parse the response as JSON
            try:
                # Clean up the response - remove any markdown code blocks or extra text
                cleaned_response = response
                if "```json" in response:
                    # Extract content between ```json and ```
                    import re
                    json_blocks = re.findall(r'```(?:json)?(.*?)```', response, re.DOTALL)
                    if json_blocks:
                        cleaned_response = json_blocks[0].strip()
                
                # Fix common JSON issues
                # 1. Replace unquoted emoji characters with quoted strings
                cleaned_response = re.sub(r'"emoji":\s*([^",}\s]+)', r'"emoji": "\1"', cleaned_response)
                
                # Parse the JSON
                result = json.loads(cleaned_response)
                
                # Ensure required fields are present
                if "valid" in result and result["valid"] == False:
                    # This is a refusal response
                    if "reason" not in result:
                        result["reason"] = "This combination is not possible."
                    
                    # Save to cache
                    self._save_to_cache(element1, element2, result)
                    return result
                
                # For valid combinations
                if "result" not in result:
                    raise ValueError("Response missing 'result' field")
                
                # Add default emoji if missing
                if "emoji" not in result:
                    result["emoji"] = "✨"
                
                # Save to cache
                self._save_to_cache(element1, element2, result)
                    
                return result
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {response}")
                
                # Try to extract information from non-JSON response
                import re
                
                # Extract result name
                result_name = None
                
                # Look for "Result:" pattern
                result_match = re.search(r'Result:?\s*([^\n]+)', response, re.IGNORECASE)
                if result_match:
                    result_name = result_match.group(1).strip()
                
                # If no result found, look for other patterns
                if not result_name:
                    # Look for patterns like "result: X" or "The result is X"
                    result_patterns = [
                        r'result[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'result is[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'would be[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'created[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'Element Name:?\s*([^\n]+)',
                        r'Name:?\s*([^\n]+)',
                        r'\*\*Name:\*\*\s*([^\n]+)',
                        r'\*\*Result:\*\*\s*([^\n]+)',
                    ]
                    
                    for pattern in result_patterns:
                        match = re.search(pattern, response, re.IGNORECASE)
                        if match:
                            result_name = match.group(1).strip()
                            break
                
                # Extract emoji
                emoji = "✨"  # Default emoji
                emoji_match = re.search(r'Emoji:?\s*([^\n]+)', response, re.IGNORECASE)
                if emoji_match:
                    emoji_text = emoji_match.group(1).strip()
                    # Extract just the emoji character if possible
                    emoji_char_match = re.search(r'([\u2600-\u27BF\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2700-\u27BF])', emoji_text)
                    if emoji_char_match:
                        emoji = emoji_char_match.group(1)
                    else:
                        emoji = emoji_text
                else:
                    # Look for emoji at the beginning of the response
                    emoji_char_match = re.search(r'^([\u2600-\u27BF\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2700-\u27BF]+)', response.strip())
                    if emoji_char_match:
                        emoji = emoji_char_match.group(1)
                    else:
                        # Look for emoji in the response
                        emoji_char_match = re.search(r'([\u2600-\u27BF\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2700-\u27BF]+)', response)
                        if emoji_char_match:
                            emoji = emoji_char_match.group(1)
                
                # If we couldn't find a result, use a default
                if not result_name:
                    # Look for any capitalized word that might be the result
                    capitalized_words = re.findall(r'\b([A-Z][a-z]+)\b', response)
                    if capitalized_words:
                        # Filter out common words and the input elements
                        common_words = ["Result", "Emoji", "Description", "Element", "Name", element1, element2]
                        filtered_words = [word for word in capitalized_words if word not in common_words]
                        if filtered_words:
                            result_name = filtered_words[0]
                
                # If still no result, try to extract from the response
                if not result_name:
                    # Split the response into lines and look for short lines that might be the result
                    lines = response.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        # Skip empty lines and lines with common words
                        if not line or any(word in line.lower() for word in ["result", "emoji", "description", "element", "name"]):
                            continue
                        # Skip lines that are too long
                        if len(line) > 30:
                            continue
                        # Skip lines with the input elements
                        if element1.lower() in line.lower() or element2.lower() in line.lower():
                            continue
                        # This might be the result
                        result_name = line
                        break
                
                # If still no result, use "Unknown"
                if not result_name:
                    result_name = "Unknown"
                
                # Clean up the result name
                result_name = result_name.strip()
                # Remove any markdown formatting
                result_name = re.sub(r'\*\*|\*|`|_', '', result_name)
                # Remove any leading/trailing punctuation
                result_name = re.sub(r'^[^\w]+|[^\w]+$', '', result_name)
                
                # Create a fallback result
                fallback = {
                    "valid": True,
                    "result": result_name,
                    "emoji": emoji,
                    "raw_response": response  # Include the raw response for debugging
                }
                
                # Save to cache
                self._save_to_cache(element1, element2, fallback)
                
                return fallback
                
        except Exception as e:
            print(f"Error in LLM service: {e}")
            fallback = {
                "valid": False,
                "reason": f"An error occurred: {str(e)}"
            }
            return fallback 