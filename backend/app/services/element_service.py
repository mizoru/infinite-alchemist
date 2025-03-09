import os
import json
from typing import List, Dict, Optional, Any
from app.models.element import Element

class ElementService:
    """Service for managing elements in the game."""
    
    def __init__(self):
        """Initialize the element service."""
        self.elements = {}
        self.combinations = {}
        self.load_elements()
    
    def load_elements(self):
        """Load elements from the database or file."""
        # For now, we'll just create some basic elements
        basic_elements = [
            Element(id=1, name="Water", emoji="💧"),
            Element(id=2, name="Fire", emoji="🔥"),
            Element(id=3, name="Earth", emoji="🌍"),
            Element(id=4, name="Air", emoji="💨"),
        ]
        
        # Add elements to the dictionary
        for element in basic_elements:
            self.elements[element.id] = element
    
    def get_element_by_id(self, element_id: int) -> Optional[Element]:
        """Get an element by its ID."""
        return self.elements.get(element_id)
    
    def get_element_by_name(self, name: str) -> Optional[Element]:
        """Get an element by its name."""
        for element in self.elements.values():
            if element.name.lower() == name.lower():
                return element
        return None
    
    def get_all_elements(self) -> List[Element]:
        """Get all elements."""
        return list(self.elements.values())
    
    def add_element(self, element: Element) -> Element:
        """Add a new element."""
        # Generate a new ID if not provided
        if element.id is None:
            element.id = max(self.elements.keys(), default=0) + 1
        
        # Add the element to the dictionary
        self.elements[element.id] = element
        return element
    
    def add_combination(self, element1_id: int, element2_id: int, result_id: int):
        """Add a new combination."""
        # Sort element IDs to ensure consistent keys
        sorted_ids = sorted([element1_id, element2_id])
        key = f"{sorted_ids[0]}:{sorted_ids[1]}"
        self.combinations[key] = result_id
    
    def get_combination(self, element1_id: int, element2_id: int) -> Optional[int]:
        """Get the result of combining two elements."""
        # Sort element IDs to ensure consistent keys
        sorted_ids = sorted([element1_id, element2_id])
        key = f"{sorted_ids[0]}:{sorted_ids[1]}"
        return self.combinations.get(key)
    
    def combine_elements(self, element1_id: int, element2_id: int) -> Optional[Element]:
        """Combine two elements to create a new one."""
        # Check if the combination already exists
        result_id = self.get_combination(element1_id, element2_id)
        if result_id:
            return self.get_element_by_id(result_id)
        
        # If not, return None (the LLM service will handle creating new combinations)
        return None 