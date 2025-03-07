#!/usr/bin/env python
"""
Script to run the prompt tester with additional combinations.
This script tests both valid combinations and combinations that should be refused.
"""

import os
import sys
import json
from pathlib import Path
import logging

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.prompt_tester import PromptTester
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the prompt tester with additional combinations."""
    logger.info("Initializing prompt tester...")
    
    # Initialize services
    prompt_service = PromptService()
    llm_service = LLMService()
    prompt_tester = PromptTester(prompt_service, llm_service)
    
    # Add more test cases to the prompt tester
    # Format: (element1, element2, expected_result)
    # If expected_result is None, the combination should be refused
    additional_test_cases = [
        # Basic elements that should combine
        ("Water", "Fire", "Steam"),
        ("Earth", "Water", "Mud"),
        ("Fire", "Earth", "Lava"),
        ("Air", "Fire", "Smoke"),
        ("Air", "Water", "Rain"),
        ("Air", "Earth", "Dust"),
        
        # More complex but valid combinations
        ("Tree", "Fire", "Charcoal"),
        ("Sand", "Fire", "Glass"),
        ("Water", "Electricity", "Electrolysis"),
        ("Metal", "Electricity", "Magnet"),
        ("Cloud", "Water", "Rain"),
        ("Sun", "Water", "Rainbow"),
        ("Flour", "Water", "Dough"),
        ("Dough", "Fire", "Bread"),
        ("Milk", "Bacteria", "Yogurt"),
        ("Grape", "Time", "Wine"),
        
        # Abstract concepts that make sense together
        ("Knowledge", "Experience", "Wisdom"),
        ("Time", "Money", "Investment"),
        ("Love", "Hate", "Passion"),
        ("Democracy", "Corruption", "Reform"),
        ("Art", "Science", "Innovation"),
        
        # Combinations that should be refused (nonsensical)
        ("Philosophy", "Doorknob", None),
        ("Quantum Physics", "Banana", None),
        ("Democracy", "Toaster", None),
        ("Existential Dread", "Paperclip", None),
        ("Consciousness", "Potato", None),
        ("Infinity", "Shoelace", None),
        ("Abstract", "Concrete", None),
        ("Nothing", "Everything", None),
        ("12345", "67890", None),
        ("", "", None),
        
        # Edge cases
        ("Element", "Element", "Redundancy"),
        ("Fire", "Fire", "Inferno"),
        ("Water", "Water", "Lake"),
        ("Earth", "Earth", "Mountain"),
        ("Air", "Air", "Wind"),
        
        # Multilingual tests (if supported)
        ("Вода", "Огонь", "Пар"),  # Water + Fire = Steam in Russian
        ("Земля", "Вода", "Грязь"),  # Earth + Water = Mud in Russian
        
        # Emoji tests
        ("😀", "😢", "Emotion"),
        ("🔥", "💧", "Steam"),
        ("🌍", "💨", "Atmosphere"),
    ]
    
    # Add the test cases to the prompt tester
    for element1, element2, expected in additional_test_cases:
        prompt_tester.add_test_case(element1, element2, expected)
    
    # Run the tests
    logger.info("Running prompt tests...")
    results = prompt_tester.test_all_prompts()
    
    # Print the results
    logger.info("Test results:")
    for language, language_results in results.items():
        for prompt_name, prompt_results in language_results.items():
            success_count = sum(1 for r in prompt_results if r.get("success", False))
            total_count = len(prompt_results)
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            logger.info(f"Language: {language}, Prompt: {prompt_name}")
            logger.info(f"Success rate: {success_rate:.2f}% ({success_count}/{total_count})")
            
            # Print details of failed tests
            failed_tests = [r for r in prompt_results if not r.get("success", False)]
            if failed_tests:
                logger.info("Failed tests:")
                for test in failed_tests:
                    element1 = test.get("element1", "Unknown")
                    element2 = test.get("element2", "Unknown")
                    expected = test.get("expected", "Unknown")
                    error = test.get("error", "No error message")
                    
                    logger.info(f"  {element1} + {element2} = {expected} (Error: {error})")
    
    logger.info("Prompt testing completed!")

if __name__ == "__main__":
    main() 