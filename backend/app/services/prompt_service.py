import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PromptService:
    """
    Service for managing and testing element combination prompts.
    This allows us to experiment with different prompts and store the best ones.
    """
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the prompt service.
        
        Args:
            prompts_dir: Directory to store prompt templates. If None, uses default location.
        """
        if prompts_dir is None:
            # Use a default directory in the app folder
            self.prompts_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
            
        # Create the directory if it doesn't exist
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # Load the default prompts
        self.default_prompts = {
            "en": self._create_default_english_prompt(),
            "ru": self._create_default_russian_prompt(),
        }
        
        # Load saved prompts if they exist
        self.prompts = self._load_prompts()
        
    def _create_default_english_prompt(self) -> str:
        """Create the default English prompt template."""
        return """
        In the game "Infinite Alchemist", players combine elements to create new ones.
        
        Given the following two elements:
        - {element1}
        - {element2}
        
        Determine what new element would be created by combining them.
        The combination should be logical and make sense based on real-world properties or common associations.
        
        Return your answer in the following JSON format:
        {{
            "result": "name of the resulting element",
            "emoji": "an appropriate emoji for the element",
            "description": "a brief description of the element"
        }}
        
        Only return the JSON, nothing else.
        """
    
    def _create_default_russian_prompt(self) -> str:
        """Create the default Russian prompt template."""
        return """
        В игре "Бесконечный Алхимик" игроки комбинируют элементы, чтобы создавать новые.
        
        Учитывая следующие два элемента:
        - {element1}
        - {element2}
        
        Определите, какой новый элемент будет создан при их комбинировании.
        Комбинация должна быть логичной и иметь смысл, основываясь на реальных свойствах или общих ассоциациях.
        
        Верните ответ в следующем JSON формате:
        {{
            "result": "название получившегося элемента",
            "emoji": "подходящий эмодзи для элемента",
            "description": "краткое описание элемента"
        }}
        
        Верните только JSON, ничего больше.
        """
    
    def _create_alternative_english_prompt(self) -> str:
        """Create an alternative English prompt based on the user's suggestion."""
        return """
        You are a helpful assistant that helps people craft new elements by combining two existing elements.
        
        Given the following two elements:
        - {element1}
        - {element2}
        
        The most important rules that you have to follow:
        1. You must NOT use the words "{element1}" and "{element2}" as part of your answer.
        2. The result must be a single noun representing a new element.
        3. The result should be related to both input elements and their context.
        4. The result can be a combination of the elements or represent the relationship between them.
        5. Results can be things, materials, people, animals, food, places, objects, concepts, phenomena, etc.
        
        Return your answer in the following JSON format:
        {{
            "result": "name of the resulting element",
            "emoji": "an appropriate emoji for the element",
            "description": "a brief description of the element"
        }}
        
        Only return the JSON, nothing else.
        """
    
    def _load_prompts(self) -> Dict[str, Dict[str, str]]:
        """
        Load saved prompts from the prompts directory.
        
        Returns:
            Dictionary of prompts by language and name.
        """
        prompts = {}
        
        # Load each JSON file in the prompts directory
        for file_path in self.prompts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lang_prompts = json.load(f)
                    lang = file_path.stem  # Use filename as language code
                    prompts[lang] = lang_prompts
            except Exception as e:
                logger.error(f"Error loading prompts from {file_path}: {e}")
        
        # If no prompts were loaded, use the defaults
        if not prompts:
            for lang, prompt in self.default_prompts.items():
                prompts[lang] = {"default": prompt}
                self._save_prompt(lang, "default", prompt)
                
            # Add the alternative prompt
            prompts["en"]["alternative"] = self._create_alternative_english_prompt()
            self._save_prompt("en", "alternative", prompts["en"]["alternative"])
        
        return prompts
    
    def _save_prompt(self, lang: str, name: str, prompt: str) -> None:
        """
        Save a prompt to the prompts directory.
        
        Args:
            lang: Language code
            name: Name of the prompt
            prompt: The prompt template
        """
        file_path = self.prompts_dir / f"{lang}.json"
        
        # Load existing prompts for this language if the file exists
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lang_prompts = json.load(f)
            except Exception:
                lang_prompts = {}
        else:
            lang_prompts = {}
        
        # Add or update the prompt
        lang_prompts[name] = prompt
        
        # Save the updated prompts
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(lang_prompts, f, ensure_ascii=False, indent=2)
    
    def get_prompt(self, lang: str = "en", name: str = "default") -> str:
        """
        Get a prompt template by language and name.
        
        Args:
            lang: Language code
            name: Name of the prompt
            
        Returns:
            The prompt template
        """
        # If the language doesn't exist, fall back to English
        if lang not in self.prompts:
            lang = "en"
            
        # If the prompt name doesn't exist, fall back to default
        if name not in self.prompts[lang]:
            name = "default"
            
        return self.prompts[lang][name]
    
    def add_prompt(self, lang: str, name: str, prompt: str) -> None:
        """
        Add a new prompt template.
        
        Args:
            lang: Language code
            name: Name of the prompt
            prompt: The prompt template
        """
        # Add to in-memory prompts
        if lang not in self.prompts:
            self.prompts[lang] = {}
        self.prompts[lang][name] = prompt
        
        # Save to file
        self._save_prompt(lang, name, prompt)
    
    def list_prompts(self, lang: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available prompts.
        
        Args:
            lang: Optional language code to filter by
            
        Returns:
            Dictionary of prompt names by language
        """
        result = {}
        
        if lang:
            if lang in self.prompts:
                result[lang] = list(self.prompts[lang].keys())
        else:
            for lang, prompts in self.prompts.items():
                result[lang] = list(prompts.keys())
                
        return result
    
    def format_prompt(self, lang: str, name: str, element1: str, element2: str) -> str:
        """
        Format a prompt template with the given elements.
        
        Args:
            lang: Language code
            name: Name of the prompt
            element1: First element
            element2: Second element
            
        Returns:
            Formatted prompt
        """
        prompt_template = self.get_prompt(lang, name)
        return prompt_template.format(element1=element1, element2=element2) 