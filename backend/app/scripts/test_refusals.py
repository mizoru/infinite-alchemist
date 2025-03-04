import sys
import json
import re
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_refusals():
    """Test refusals directly with a specialized prompt."""
    # Initialize the LLM
    api_key = os.getenv("LLM_API_KEY")
    model_name = os.getenv("LLM_MODEL", "lightblue/suzume-llama-3-8B-multilingual")
    
    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is not set")
    
    llm = HuggingFaceEndpoint(
        endpoint_url=f"https://api-inference.huggingface.co/models/{model_name}",
        huggingfacehub_api_token=api_key,
        task="text-generation",
        model_kwargs={
            "temperature": 0.2,  # Lower temperature for more consistent results
            "max_new_tokens": 150,
            "do_sample": True,
        }
    )
    
    # Define a specialized prompt for testing refusals
    refusal_prompt = PromptTemplate(
        input_variables=["element1", "element2"],
        template="""
        You are a strict validator for the game "Infinite Alchemist". Your job is to determine if two elements can be combined.
        
        RULES:
        1. Elements can only be combined if they have a clear, logical relationship.
        2. Physical elements (like Water, Fire, Earth) can usually be combined.
        3. Abstract concepts (like Love, Democracy, Philosophy) CANNOT be combined with physical elements.
        4. Elements from completely different domains with no connection CANNOT be combined.
        5. Nonsensical combinations MUST be rejected.
        
        Elements to validate:
        - {element1}
        - {element2}
        
        Respond ONLY with this JSON format:
        
        If the combination is valid:
        ```json
        {{
            "valid": true,
            "result": "name of resulting element",
            "emoji": "appropriate emoji"
        }}
        ```
        
        If the combination is invalid:
        ```json
        {{
            "valid": false,
            "reason": "brief explanation why this combination is invalid"
        }}
        ```
        """
    )
    
    # Test combinations - mix of valid and nonsensical
    test_combinations = [
        # Valid combinations
        ("Water", "Fire"),
        ("Earth", "Fire"),
        ("Water", "Earth"),
        ("Air", "Fire"),
        
        # Potentially valid but unusual
        ("Gold", "Silver"),
        ("Tree", "Axe"),
        
        # Nonsensical combinations
        ("Happiness", "Bureaucracy"),
        ("Internet", "Dinosaur"),
        ("Quantum", "Banana"),
        ("Democracy", "Toaster"),
        ("Abstract", "Concrete"),
        ("Nothing", "Everything"),
        
        # Extremely nonsensical combinations
        ("Existential Dread", "Paperclip"),
        ("Quantum Mechanics", "Cheese"),
        ("Philosophy", "Blender"),
        ("Metaphysics", "Doorknob"),
        ("Consciousness", "Potato"),
        ("Infinity", "Shoelace"),
    ]
    
    print("Testing refusals with specialized prompt...")
    
    valid_count = 0
    invalid_count = 0
    
    for element1, element2 in test_combinations:
        print(f"\nValidating {element1} + {element2}:")
        
        # Format the prompt
        formatted_prompt = refusal_prompt.format(element1=element1, element2=element2)
        
        # Get the response
        response = llm(formatted_prompt)
        print(f"Raw response: {response}")
        
        # Try to parse the JSON
        try:
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
            else:
                result = json.loads(response)
            
            # Print the result
            if result.get("valid", False):
                valid_count += 1
                print(f"  VALID: {result.get('result', 'No result')} {result.get('emoji', '')}")
            else:
                invalid_count += 1
                print(f"  INVALID: {result.get('reason', 'No reason provided')}")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Error parsing response: {e}")
    
    print(f"\nResults: {valid_count} valid combinations, {invalid_count} invalid combinations")

if __name__ == "__main__":
    test_refusals() 