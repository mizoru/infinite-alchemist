#!/usr/bin/env python
"""
Script to test different prompts for element combinations and find the best one.
This can be run as a standalone script to evaluate prompts before deploying them.
"""

import os
import sys
import json
import time
from pathlib import Path
from tqdm import tqdm

# Add the parent directory to the path so we can import the app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.prompt_service import PromptService
from app.services.prompt_tester import PromptTester
from app.services.llm_service import LLMService

def create_test_prompts():
    """Create test prompts for different languages and styles."""
    prompt_service = PromptService()
    
    # English prompts
    
    # Default prompt - standard format
    prompt_service.add_prompt("en", "default", """
    In the game "Infinite Alchemist", players combine elements to create new ones.
    
    Given the following two elements:
    - {element1}
    - {element2}
    
    Determine what new element would be created by combining them.
    The combination should be logical and make sense based on real-world properties or common associations.
    
    Return your answer in the following format:
    
    ```json
    {{
        "result": "name of the resulting element",
        "emoji": "an appropriate emoji for the element"
    }}
    ```
    
    Only return the JSON, nothing else.
    """)
    
    # User example prompt - with examples
    prompt_service.add_prompt("en", "user_example", """
    In the game "Infinite Alchemist", I need to combine two elements to create a new one.
    
    The rules are:
    1. The new element should be a logical combination of the two input elements
    2. The new element's name should NOT contain the names of the input elements
    3. The result should be creative but make sense
    
    For example:
    - Water + Fire = Steam
    - Earth + Water = Mud
    - Air + Fire = Smoke
    
    Now I want to combine these elements:
    - {element1}
    - {element2}
    
    What would be the resulting element? Please provide the name and an appropriate emoji in JSON format:
    
    ```json
    {{
        "result": "name of the resulting element",
        "emoji": "an appropriate emoji for the element"
    }}
    ```
    """)
    
    # Concise prompt - minimal instructions
    prompt_service.add_prompt("en", "concise", """
    Combine these elements in the Infinite Alchemist game:
    - {element1}
    - {element2}
    
    Return only JSON:
    
    ```json
    {{
        "result": "name of the resulting element",
        "emoji": "an appropriate emoji for the element"
    }}
    ```
    """)
    
    # Game-focused prompt
    prompt_service.add_prompt("en", "game", """
    You're playing "Infinite Alchemist", a game where you combine elements to discover new ones.
    
    You're combining:
    - {element1}
    - {element2}
    
    What new element do you discover? The combination should follow logical rules and not contain the names of the original elements.
    
    Return only this JSON:
    
    ```json
    {{
        "result": "name of the resulting element",
        "emoji": "an appropriate emoji for the element"
    }}
    ```
    """)
    
    # Simple prompt - very direct
    prompt_service.add_prompt("en", "simple", """
    What would you get if you combined {element1} and {element2}?
    
    Return only this JSON:
    
    ```json
    {{
        "result": "name of the resulting element",
        "emoji": "an appropriate emoji for the element"
    }}
    ```
    """)
    
    # Russian prompt (default)
    prompt_service.add_prompt("ru", "default", """
    В игре "Бесконечный Алхимик" игроки комбинируют элементы, чтобы создавать новые.
    
    Даны следующие два элементы:
    - {element1}
    - {element2}
    
    Определите, какой новый элемент будет создан при их комбинировании.
    Комбинация должна быть логичной и иметь смысл, основываясь на реальных свойствах или общих ассоциациях.
    
    Верните ответ только в формате JSON:
    
    ```json
    {{
        "result": "название полученного элемента",
        "emoji": "подходящий эмодзи для элемента"
    }}
    ```
    """)
    
    # Print the created prompts
    prompts = prompt_service.list_prompts()
    print("Created test prompts:")
    print(json.dumps(prompts, indent=2))
    
    return prompt_service

def test_prompts():
    """Test different prompts and evaluate their performance."""
    # Initialize services
    prompt_service = PromptService()
    prompt_tester = PromptTester(prompt_service=prompt_service)
    
    # Clear existing test cases and add a smaller set
    prompt_tester.clear_test_cases()
    
    # Add a few key test cases
    prompt_tester.add_test_case("Water", "Fire", "Steam")
    prompt_tester.add_test_case("Earth", "Fire", "Lava")
    prompt_tester.add_test_case("Water", "Earth", "Mud")
    prompt_tester.add_test_case("Nonsense", "Gibberish", None)
    
    # Test only specific prompts
    test_prompts = ["default", "user_example", "concise", "game", "simple"]
    results = []
    
    print("Testing prompts...")
    
    # Calculate total iterations for progress bar
    total_iterations = len(test_prompts) * len(prompt_tester.test_cases)
    
    # Create progress bar
    with tqdm(total=total_iterations, desc="Testing prompts", unit="test") as pbar:
        for prompt_name in test_prompts:
            print(f"\nTesting {prompt_name}...")
            
            # Test each case with this prompt
            result = {
                "lang": "en",
                "name": prompt_name,
                "test_cases": [],
                "success_rate": 0.0,
                "errors": 0,
                "invalid_json": 0,
            }
            
            total_tests = len(prompt_tester.test_cases)
            successful_tests = 0
            
            # Create a directory for this prompt's results
            results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "results")
            os.makedirs(results_dir, exist_ok=True)
            prompt_results_dir = os.path.join(results_dir, f"en_{prompt_name}")
            os.makedirs(prompt_results_dir, exist_ok=True)
            
            for element1, element2, expected in prompt_tester.test_cases:
                # Format the prompt
                try:
                    formatted_prompt = prompt_service.format_prompt("en", prompt_name, element1, element2)
                    
                    # Save the formatted prompt to a file
                    prompt_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_prompt.txt")
                    with open(prompt_file, "w", encoding="utf-8") as f:
                        f.write(formatted_prompt)
                    
                    # Get the response
                    response = prompt_tester.llm_service._get_llm_response(formatted_prompt)
                    
                    # Save the raw response to a file
                    response_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_response.txt")
                    with open(response_file, "w", encoding="utf-8") as f:
                        f.write(response)
                    
                    # Process the response
                    test_case_result = prompt_tester._process_response(element1, element2, expected, response, prompt_results_dir)
                    result["test_cases"].append(test_case_result)
                    
                    if test_case_result.get("success", False):
                        successful_tests += 1
                    if "error" in test_case_result and "Invalid JSON" in test_case_result["error"]:
                        result["invalid_json"] += 1
                    elif "error" in test_case_result:
                        result["errors"] += 1
                        
                except Exception as e:
                    print(f"Error testing {element1} + {element2}: {e}")
                    result["test_cases"].append({
                        "element1": element1,
                        "element2": element2,
                        "expected": expected,
                        "result": None,
                        "error": str(e),
                        "success": False,
                    })
                    result["errors"] += 1
                
                # Update progress bar
                pbar.update(1)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Calculate success rate
            if total_tests > 0:
                result["success_rate"] = successful_tests / total_tests
                
            # Save the overall results
            overall_results_file = os.path.join(prompt_results_dir, "overall_results.json")
            with open(overall_results_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
                
            results.append(result)
    
    # Sort results by success rate
    results.sort(key=lambda x: x["success_rate"], reverse=True)
    
    print("\nResults:")
    for result in results:
        print(f"\n{result['lang']}/{result['name']}:")
        print(f"  Success rate: {result['success_rate']:.2f}")
        print(f"  Errors: {result['errors']}")
        print(f"  Invalid JSON: {result['invalid_json']}")
    
    # Find the best prompt
    if results:
        best_prompt = max(results, key=lambda x: x["success_rate"])
        print(f"\nBest prompt: {best_prompt['lang']}/{best_prompt['name']} with success rate {best_prompt['success_rate']:.2f}")
        
        # Print some example results from the best prompt
        print("\nExample results from best prompt:")
        for test_case in best_prompt["test_cases"]:
            if test_case.get("success", False) and test_case.get("result"):
                print(f"\n{test_case['element1']} + {test_case['element2']} = {test_case['result'].get('result', 'Unknown')}")
                print(f"  Emoji: {test_case['result'].get('emoji', '❓')}")
    else:
        print("\nNo results available.")
    
    # Save detailed results to a file
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    results_file = os.path.join(results_dir, "prompt_test_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to {results_file}")
    
    return results

def main():
    """Main function to run the script."""
    # Create test prompts
    create_test_prompts()
    
    # Test the prompts
    test_prompts()

if __name__ == "__main__":
    main() 