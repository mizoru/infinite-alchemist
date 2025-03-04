from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any

from app.db.database import get_db
from app.services.prompt_service import PromptService
from app.services.prompt_tester import PromptTester
from pydantic import BaseModel

router = APIRouter()
prompt_service = PromptService()
prompt_tester = PromptTester(prompt_service=prompt_service)

class PromptCreate(BaseModel):
    lang: str
    name: str
    prompt: str

class TestCase(BaseModel):
    element1: str
    element2: str
    expected: Optional[str] = None

class TestPromptRequest(BaseModel):
    lang: str
    name: str
    test_cases: Optional[List[TestCase]] = None

@router.get("/")
def list_prompts(lang: Optional[str] = None):
    """
    List all available prompts.
    """
    return prompt_service.list_prompts(lang)

@router.get("/{lang}/{name}")
def get_prompt(lang: str, name: str):
    """
    Get a specific prompt.
    """
    try:
        return {"prompt": prompt_service.get_prompt(lang, name)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {str(e)}")

@router.post("/")
def create_prompt(prompt: PromptCreate):
    """
    Create a new prompt.
    """
    try:
        prompt_service.add_prompt(prompt.lang, prompt.name, prompt.prompt)
        return {"status": "success", "message": f"Prompt {prompt.lang}/{prompt.name} created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create prompt: {str(e)}")

@router.post("/test")
def test_prompt(request: TestPromptRequest):
    """
    Test a prompt with various element combinations.
    """
    # If custom test cases are provided, use them
    if request.test_cases:
        # Save the original test cases
        original_test_cases = prompt_tester.test_cases.copy()
        
        # Set the custom test cases
        prompt_tester.clear_test_cases()
        for test_case in request.test_cases:
            prompt_tester.add_test_case(test_case.element1, test_case.element2, test_case.expected)
        
        # Run the test
        result = prompt_tester.test_prompt(request.lang, request.name)
        
        # Restore the original test cases
        prompt_tester.test_cases = original_test_cases
    else:
        # Use the default test cases
        result = prompt_tester.test_prompt(request.lang, request.name)
    
    return result

@router.post("/test/all")
def test_all_prompts(lang: Optional[str] = None):
    """
    Test all available prompts and return the results.
    """
    results = prompt_tester.test_all_prompts(lang)
    return results

@router.post("/test/add-case")
def add_test_case(test_case: TestCase):
    """
    Add a new test case for prompt testing.
    """
    prompt_tester.add_test_case(test_case.element1, test_case.element2, test_case.expected)
    return {"status": "success", "message": "Test case added", "test_cases_count": len(prompt_tester.test_cases)}

@router.post("/test/clear-cases")
def clear_test_cases():
    """
    Clear all test cases.
    """
    prompt_tester.clear_test_cases()
    return {"status": "success", "message": "Test cases cleared"}

@router.post("/combine")
def combine_elements_with_prompt(
    element1: str = Body(...),
    element2: str = Body(...),
    lang: str = Body("en"),
    prompt_name: str = Body("default")
):
    """
    Combine two elements using a specific prompt.
    """
    from app.services.llm_service import LLMService
    llm_service = LLMService()
    
    result = llm_service.combine_elements(element1, element2, lang, prompt_name)
    return result 