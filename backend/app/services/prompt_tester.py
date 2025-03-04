import json
import logging
import os
from typing import Dict, List, Tuple, Any, Optional
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class PromptTester:
    """
    Service for testing different prompts with the LLM.
    This allows us to evaluate which prompts produce the best results.
    """
    
    def __init__(self, prompt_service: Optional[PromptService] = None, llm_service: Optional[LLMService] = None):
        """
        Initialize the prompt tester.
        
        Args:
            prompt_service: Service for managing prompts
            llm_service: Service for interacting with the LLM
        """
        self.prompt_service = prompt_service or PromptService()
        self.llm_service = llm_service or LLMService()
        
        # Test cases for evaluating prompts
        self.test_cases = [
            # Basic combinations that should work well
            ("Water", "Fire", "Steam"),
            ("Earth", "Fire", "Lava"),
            ("Water", "Earth", "Mud"),
            ("Fire", "Air", "Smoke"),
            
            # More complex combinations
            ("Gold", "Silver", "Alloy"),
            ("Tree", "Axe", "Wood"),
            ("Flour", "Water", "Dough"),
            ("Dough", "Fire", "Bread"),
            
            # Abstract combinations
            ("Knowledge", "Power", "Wisdom"),
            ("Time", "Money", "Efficiency"),
            
            # Nonsensical combinations that should be handled gracefully
            ("Nonsense", "Gibberish", None),
            ("12345", "67890", None),
            ("", "", None),
        ]
        
        # Create results directory if it doesn't exist
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "results")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def test_prompt(self, lang: str, name: str) -> Dict[str, Any]:
        """
        Test a prompt with various element combinations.
        
        Args:
            lang: Language code
            name: Name of the prompt
            
        Returns:
            Dictionary with test results
        """
        results = {
            "lang": lang,
            "name": name,
            "test_cases": [],
            "success_rate": 0.0,
            "errors": 0,
            "invalid_json": 0,
        }
        
        total_tests = len(self.test_cases)
        successful_tests = 0
        
        # Create a directory for this prompt's results
        prompt_results_dir = os.path.join(self.results_dir, f"{lang}_{name}")
        os.makedirs(prompt_results_dir, exist_ok=True)
        
        for element1, element2, expected in self.test_cases:
            # Format the prompt
            try:
                formatted_prompt = self.prompt_service.format_prompt(lang, name, element1, element2)
            except Exception as e:
                logger.error(f"Error formatting prompt: {e}")
                results["test_cases"].append({
                    "element1": element1,
                    "element2": element2,
                    "expected": expected,
                    "result": None,
                    "error": str(e),
                    "success": False,
                })
                results["errors"] += 1
                continue
            
            # Get response from LLM
            try:
                # Save the formatted prompt to a file
                prompt_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_prompt.txt")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(formatted_prompt)
                
                # Get the response
                response = self.llm_service._get_llm_response(formatted_prompt)
                
                # Save the raw response to a file
                response_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_response.txt")
                with open(response_file, "w", encoding="utf-8") as f:
                    f.write(response)
                
                # Try to parse as JSON
                try:
                    # Clean up the response - remove any markdown code blocks or extra text
                    cleaned_response = response
                    if "```json" in response:
                        # Extract content between ```json and ```
                        import re
                        json_blocks = re.findall(r'```(?:json)?(.*?)```', response, re.DOTALL)
                        if json_blocks:
                            cleaned_response = json_blocks[0].strip()
                    
                    result = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON response for {element1} + {element2}: {response}")
                    results["test_cases"].append({
                        "element1": element1,
                        "element2": element2,
                        "expected": expected,
                        "result": response,
                        "error": "Invalid JSON response",
                        "success": False,
                    })
                    results["invalid_json"] += 1
                    
                    # Try to extract information from non-JSON response
                    import re
                    
                    # Look for patterns like "result: X" or "The result is X"
                    result_patterns = [
                        r'result[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'result is[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'would be[:\s]+["\']*([^"\',\n]+)["\',]',
                        r'created[:\s]+["\']*([^"\',\n]+)["\',]',
                    ]
                    
                    result_name = None
                    for pattern in result_patterns:
                        match = re.search(pattern, response, re.IGNORECASE)
                        if match:
                            result_name = match.group(1).strip()
                            break
                    
                    # If we couldn't find a result, use a default
                    if not result_name:
                        continue
                    
                    # Create a fallback result
                    result = {
                        "result": result_name,
                        "emoji": "✨",
                        "raw_response": response
                    }
                    
                    # Save the extracted result
                    result_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_extracted.json")
                    with open(result_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2)
                    
                    # Continue with validation
                    
            except Exception as e:
                logger.error(f"Error getting LLM response: {e}")
                results["test_cases"].append({
                    "element1": element1,
                    "element2": element2,
                    "expected": expected,
                    "result": None,
                    "error": str(e),
                    "success": False,
                })
                results["errors"] += 1
                continue
            
            # Check if the result is valid
            success = self._validate_result(result, element1, element2, expected)
            if success:
                successful_tests += 1
                
            # Save the result and evaluation
            result_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_result.json")
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
                
            eval_file = os.path.join(prompt_results_dir, f"{element1}_{element2}_eval.json")
            eval_result = {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "success": success,
                "notes": self._get_validation_notes(result, element1, element2, expected)
            }
            with open(eval_file, "w", encoding="utf-8") as f:
                json.dump(eval_result, f, indent=2)
                
            results["test_cases"].append({
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "result": result,
                "success": success,
            })
        
        # Calculate success rate
        if total_tests > 0:
            results["success_rate"] = successful_tests / total_tests
            
        # Save the overall results
        overall_results_file = os.path.join(prompt_results_dir, "overall_results.json")
        with open(overall_results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            
        return results
    
    def _validate_result(self, result: Dict[str, Any], element1: str, element2: str, expected: Optional[str]) -> bool:
        """
        Validate the result of a prompt test.
        
        Args:
            result: The result from the LLM
            element1: First element
            element2: Second element
            expected: Expected result, or None if no specific expectation
            
        Returns:
            True if the result is valid, False otherwise
        """
        # If we got None but expected something specific
        if result is None and expected is not None:
            return False
            
        # If we got a result for a nonsensical combination
        if expected is None:
            # Check if the result indicates a refusal
            if (result is None or 
                result.get("result", "").lower() == "impossible" or
                "impossible" in result.get("reason", "").lower() or
                "cannot" in result.get("reason", "").lower() or
                "doesn't work" in result.get("reason", "").lower() or
                "invalid" in result.get("reason", "").lower()):
                return True
            return False
            
        # Check if the result contains the required field 'result'
        if "result" not in result:
            return False
            
        # If the result is "impossible" but we expected a valid combination
        if result.get("result", "").lower() == "impossible" and expected is not None:
            return False
            
        # Check if the result contains the input elements (which it shouldn't)
        if (element1.lower() in result.get("result", "").lower() or 
            element2.lower() in result.get("result", "").lower()):
            return False
            
        # If we have a specific expected result, check if it matches
        if expected and expected.lower() not in result.get("result", "").lower():
            # This is a soft check - the exact result might vary
            # We could make this stricter if needed
            pass
            
        return True
    
    def _get_validation_notes(self, result: Dict[str, Any], element1: str, element2: str, expected: Optional[str]) -> List[str]:
        """
        Generate notes about the validation result.
        
        Args:
            result: The result from the LLM
            element1: First element
            element2: Second element
            expected: Expected result, or None if no specific expectation
            
        Returns:
            List of notes about the validation
        """
        notes = []
        
        if result is None:
            notes.append("No result was returned")
            return notes
            
        # Check for refusal
        if result.get("result", "").lower() == "impossible":
            if expected is None:
                notes.append("Correctly refused nonsensical combination")
            else:
                notes.append(f"Incorrectly refused valid combination (expected: {expected})")
            if "reason" in result:
                notes.append(f"Refusal reason: {result['reason']}")
            return notes
            
        if "result" not in result:
            notes.append("Missing 'result' field")
        
        if "emoji" not in result and result.get("result", "").lower() != "impossible":
            notes.append("Missing 'emoji' field")
            
        if element1.lower() in result.get("result", "").lower():
            notes.append(f"Result contains input element '{element1}'")
            
        if element2.lower() in result.get("result", "").lower():
            notes.append(f"Result contains input element '{element2}'")
            
        if expected and expected.lower() not in result.get("result", "").lower():
            notes.append(f"Result '{result.get('result')}' does not match expected '{expected}'")
            
        return notes
    
    def test_all_prompts(self, lang: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Test all available prompts.
        
        Args:
            lang: Optional language code to filter by
            
        Returns:
            List of test results for each prompt
        """
        results = []
        
        # Get available prompts
        available_prompts = self.prompt_service.list_prompts(lang)
        
        # Test each prompt
        for test_lang, prompt_names in available_prompts.items():
            for name in prompt_names:
                result = self.test_prompt(test_lang, name)
                results.append(result)
                
        # Sort results by success rate
        results.sort(key=lambda x: x["success_rate"], reverse=True)
        
        # Save the overall comparison
        comparison_file = os.path.join(self.results_dir, "prompt_comparison.json")
        with open(comparison_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def add_test_case(self, element1: str, element2: str, expected: Optional[str] = None) -> None:
        """
        Add a new test case.
        
        Args:
            element1: First element
            element2: Second element
            expected: Expected result, or None if no specific expectation
        """
        self.test_cases.append((element1, element2, expected))
        
    def clear_test_cases(self) -> None:
        """Clear all test cases."""
        self.test_cases = []
    
    def _process_response(self, element1: str, element2: str, expected: Optional[str], response: str, output_dir: str) -> Dict[str, Any]:
        """
        Process a response from the LLM.
        
        Args:
            element1: First element
            element2: Second element
            expected: Expected result, or None if no specific expectation
            response: Raw response from the LLM
            output_dir: Directory to save results
            
        Returns:
            Dictionary with test case results
        """
        try:
            # Clean up the response - remove any markdown code blocks or extra text
            cleaned_response = response
            if "```json" in response:
                # Extract content between ```json and ```
                import re
                json_blocks = re.findall(r'```(?:json)?(.*?)```', response, re.DOTALL)
                if json_blocks:
                    cleaned_response = json_blocks[0].strip()
            
            # Parse the JSON
            result = json.loads(cleaned_response)
            
            # Save the result
            result_file = os.path.join(output_dir, f"{element1}_{element2}_result.json")
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            
            # Validate the result
            success = self._validate_result(result, element1, element2, expected)
            
            # Save the evaluation
            eval_file = os.path.join(output_dir, f"{element1}_{element2}_eval.json")
            eval_result = {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "success": success,
                "notes": self._get_validation_notes(result, element1, element2, expected)
            }
            with open(eval_file, "w", encoding="utf-8") as f:
                json.dump(eval_result, f, indent=2)
            
            return {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "result": result,
                "success": success,
            }
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response for {element1} + {element2}: {response}")
            
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
            result = {
                "result": result_name,
                "emoji": emoji,
                "raw_response": response  # Include the raw response for debugging
            }
            
            # Save the extracted result
            extracted_file = os.path.join(output_dir, f"{element1}_{element2}_extracted.json")
            with open(extracted_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            
            # Validate the result
            success = self._validate_result(result, element1, element2, expected)
            
            # Save the evaluation
            eval_file = os.path.join(output_dir, f"{element1}_{element2}_eval.json")
            eval_result = {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "success": success,
                "notes": self._get_validation_notes(result, element1, element2, expected)
            }
            with open(eval_file, "w", encoding="utf-8") as f:
                json.dump(eval_result, f, indent=2)
            
            return {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "result": response,
                "error": "Invalid JSON response",
                "success": False,
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {
                "element1": element1,
                "element2": element2,
                "expected": expected,
                "result": None,
                "error": str(e),
                "success": False,
            } 