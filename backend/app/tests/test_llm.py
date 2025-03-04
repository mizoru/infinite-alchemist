import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

def test_huggingface_connection():
    # Load environment variables
    load_dotenv()
    
    API_TOKEN = os.getenv("LLM_API_KEY")
    MODEL_ID = os.getenv("LLM_MODEL")
    
    # Initialize the client
    client = InferenceClient(model=MODEL_ID, api_key=API_TOKEN)
    
    # Test messages including a combination prompt
    messages = [
        {
            "role": "user",
            "content": "If I combine Water and Fire, what element would I get? Please respond in Russian."
        }
    ]
    
    try:
        print("Starting chat completion...")
        stream = client.chat.completions.create(
            messages=messages,
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            stream=True
        )
        
        print("\nResponse from model:")
        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        print("\n")
        
        return True
    except Exception as e:
        print(f"Error testing HuggingFace connection: {e}")
        return False

if __name__ == "__main__":
    test_huggingface_connection() 