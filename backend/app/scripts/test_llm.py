import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the LLM service
from app.services.llm_service import LLMService

def main():
    """Test the LLM service with some basic combinations."""
    print("Testing LLM service...")
    
    # Initialize the LLM service
    llm_service = LLMService()
    
    # Test some basic combinations
    test_combinations = [
        ("Water", "Fire"),
        ("Earth", "Fire"),
        ("Water", "Earth"),
        ("Air", "Fire"),
        ("Happiness", "Bureaucracy"),
        ("Internet", "Dinosaur"),
        ("Quantum", "Banana"),
        ("Democracy", "Toaster"),
        ("Nothing", "Everything"),
    ]
    
    # Test each combination
    for element1, element2 in test_combinations:
        print(f"\nCombining {element1} + {element2}:")
        result = llm_service.combine_elements(element1, element2)
        
        if "valid" in result and result["valid"] == False:
            print(f"  IMPOSSIBLE: {result.get('reason', 'No reason provided')}")
        else:
            print(f"  Result: {result.get('result', 'Unknown')} {result.get('emoji', '✨')}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 