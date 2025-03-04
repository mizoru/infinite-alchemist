import sys
import os
import json
import re
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the Element model
from app.models.element_model import Element

class MockLLMService:
    """Mock LLM service for testing."""
    
    def __init__(self):
        """Initialize the mock LLM service."""
        # Define some predefined responses
        self.responses = {
            "Fire:Water": {
                "valid": True,
                "result": "Steam",
                "emoji": "💨"
            },
            "Earth:Fire": {
                "valid": True,
                "result": "Magma",
                "emoji": "🌋"
            },
            "Earth:Water": {
                "valid": True,
                "result": "Mud",
                "emoji": "🥾"
            },
            "Air:Fire": {
                "valid": True,
                "result": "Smoke",
                "emoji": "🌫️"
            },
            "Love:Pizza": {
                "valid": False,
                "reason": "Abstract concepts cannot be combined with physical elements."
            },
            "Computer:Knowledge": {
                "valid": False,
                "reason": "Abstract concepts cannot be combined with physical elements."
            },
            "Time:Water": {
                "valid": False,
                "reason": "Abstract concepts cannot be combined with physical elements."
            },
            "Earth:Music": {
                "valid": False,
                "reason": "Abstract concepts cannot be combined with physical elements."
            }
        }
    
    def combine_elements(self, element1, element2, prompt_type="default", language="en"):
        """Combine two elements to create a new one."""
        # Sort elements to ensure consistent keys
        sorted_elements = sorted([element1, element2])
        key = f"{sorted_elements[0]}:{sorted_elements[1]}"
        
        # Return predefined response if available
        if key in self.responses:
            return self.responses[key]
        
        # For unknown combinations, determine if they're valid based on rules
        if (element1 in ["Love", "Knowledge", "Time", "Music"] or 
            element2 in ["Love", "Knowledge", "Time", "Music"]):
            return {
                "valid": False,
                "reason": "Abstract concepts cannot be combined with physical elements."
            }
        
        # Default to a valid combination
        return {
            "valid": True,
            "result": f"{element1}{element2}",
            "emoji": "✨"
        }

def test_game_api():
    """Test the game API with our mock LLM service."""
    print("Testing game API with mock LLM service...\n")
    
    # Initialize services
    llm_service = MockLLMService()
    
    # Create some basic elements
    basic_elements = [
        Element(id=1, name="Water", emoji="💧", description="A clear liquid essential for life"),
        Element(id=2, name="Fire", emoji="🔥", description="Heat and light produced by burning"),
        Element(id=3, name="Earth", emoji="🌍", description="The ground beneath our feet"),
        Element(id=4, name="Air", emoji="💨", description="The invisible gas we breathe"),
    ]
    
    # Add some abstract concepts
    abstract_elements = [
        Element(id=5, name="Love", emoji="❤️", description="A deep affection"),
        Element(id=6, name="Knowledge", emoji="📚", description="Information and skills acquired through experience or education"),
        Element(id=7, name="Time", emoji="⏰", description="The indefinite continued progress of existence"),
    ]
    
    # Add some random elements
    random_elements = [
        Element(id=8, name="Pizza", emoji="🍕", description="A savory dish of Italian origin"),
        Element(id=9, name="Computer", emoji="💻", description="An electronic device for processing data"),
        Element(id=10, name="Music", emoji="🎵", description="Vocal or instrumental sounds combined in harmony"),
    ]
    
    # Combine all elements
    all_elements = basic_elements + abstract_elements + random_elements
    
    # Test valid combinations
    valid_combinations = [
        ("Water", "Fire"),
        ("Earth", "Fire"),
        ("Water", "Earth"),
        ("Air", "Fire"),
    ]
    
    # Test invalid combinations
    invalid_combinations = [
        ("Love", "Pizza"),
        ("Knowledge", "Computer"),
        ("Time", "Water"),
        ("Music", "Earth"),
    ]
    
    # Test all combinations
    print("Testing valid combinations:")
    for element1, element2 in valid_combinations:
        result = llm_service.combine_elements(element1, element2)
        print(f"  {element1} + {element2} = ", end="")
        if result.get("valid", True):
            print(f"{result.get('result', 'Unknown')} {result.get('emoji', '✨')}")
        else:
            print(f"INVALID: {result.get('reason', 'No reason provided')}")
    
    print("\nTesting invalid combinations:")
    for element1, element2 in invalid_combinations:
        result = llm_service.combine_elements(element1, element2)
        print(f"  {element1} + {element2} = ", end="")
        if result.get("valid", True):
            print(f"{result.get('result', 'Unknown')} {result.get('emoji', '✨')}")
        else:
            print(f"INVALID: {result.get('reason', 'No reason provided')}")
    
    print("\nTesting element discovery:")
    # Simulate discovering new elements
    discovered = []
    for i in range(min(5, len(all_elements))):
        element = all_elements[i]
        print(f"  Discovered: {element.name} {element.emoji}")
        discovered.append(element)
    
    print("\nTesting element combination in game context:")
    # Simulate combining elements in game context
    if len(discovered) >= 2:
        element1 = discovered[0]
        element2 = discovered[1]
        result = llm_service.combine_elements(element1.name, element2.name)
        print(f"  {element1.name} {element1.emoji} + {element2.name} {element2.emoji} = ", end="")
        if result.get("valid", True):
            new_element = Element(
                id=len(all_elements) + 1,
                name=result.get("result", "Unknown"),
                emoji=result.get("emoji", "✨"),
                description=result.get("description", "A new element"),
            )
            print(f"{new_element.name} {new_element.emoji}")
            discovered.append(new_element)
        else:
            print(f"INVALID: {result.get('reason', 'No reason provided')}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_game_api() 