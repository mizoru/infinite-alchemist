from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Element:
    """Model representing an element in the game."""
    
    id: Optional[int] = None
    name: str = ""
    emoji: str = "✨"
    discovered: bool = True
    created_by: Optional[str] = None
    created_from: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the element to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "discovered": self.discovered,
            "created_by": self.created_by,
            "created_from": self.created_from,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Element':
        """Create an element from a dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            emoji=data.get("emoji", "✨"),
            discovered=data.get("discovered", True),
            created_by=data.get("created_by"),
            created_from=data.get("created_from", []),
        ) 