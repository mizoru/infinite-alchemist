from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Association table for element combinations
element_combinations = Table(
    "element_combinations",
    Base.metadata,
    Column("element1_id", Integer, ForeignKey("elements.id"), primary_key=True),
    Column("element2_id", Integer, ForeignKey("elements.id"), primary_key=True),
    Column("result_id", Integer, ForeignKey("elements.id"), primary_key=True),
    Column("language", String, primary_key=True),  # "en", "ru", etc.
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("discovered_by", String, nullable=True),
)

# Association table for player-unlocked elements
player_elements = Table(
    "player_elements",
    Base.metadata,
    Column("player_name", String, primary_key=True),
    Column("element_id", Integer, ForeignKey("elements.id"), primary_key=True),
    Column("unlocked_at", DateTime(timezone=True), server_default=func.now()),
)

class DBElement(Base):
    """SQLAlchemy model for the elements table."""
    __tablename__ = "elements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    emoji = Column(String, default="✨")
    is_basic = Column(Boolean, default=False)
    language = Column(String, default="en", index=True)  # "en", "ru", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    
    # Relationships
    discovered_by = relationship("DiscoveryHistory", back_populates="element")
    
    def __repr__(self):
        return f"<Element(id={self.id}, name='{self.name}', language='{self.language}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the database model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "is_basic": self.is_basic,
            "language": self.language,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }

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

class PlayerStats(Base):
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, unique=True, index=True)
    elements_discovered = Column(Integer, default=0)  # First to discover globally
    elements_unlocked = Column(Integer, default=0)    # Personally unlocked
    combinations_tried = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional statistics can be added here as needed
    successful_combinations = Column(Integer, default=0)
    failed_combinations = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<PlayerStats(player_name='{self.player_name}', elements_discovered={self.elements_discovered})>"

# Discovery history to track when elements were discovered
class DiscoveryHistory(Base):
    __tablename__ = "discovery_history"
    
    id = Column(Integer, primary_key=True, index=True)
    element_id = Column(Integer, ForeignKey("elements.id"), index=True)
    player_name = Column(String, index=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    is_first_discovery = Column(Boolean, default=False)  # Whether this was the first global discovery
    
    # Relationship to the element
    element = relationship("DBElement", back_populates="discovered_by")
    
    def __repr__(self):
        return f"<DiscoveryHistory(element_id={self.element_id}, player_name='{self.player_name}')>" 