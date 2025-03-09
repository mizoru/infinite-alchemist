from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from datetime import datetime

class ElementBase(BaseModel):
    name: str
    emoji: Optional[str] = None
    is_basic: Union[int, bool] = False
    language: str = "en"  # "en", "ru", etc.

class ElementCreate(ElementBase):
    pass

class CombinationRequest(BaseModel):
    element1_id: int
    element2_id: int
    player_name: Optional[str] = None
    lang: str = "en"  # Default to English
    prompt_name: str = "default"  # Default prompt template

    class Config:
        json_schema_extra = {
            "example": {
                "element1_id": 1,
                "element2_id": 2,
                "player_name": "player123",
                "lang": "ru",  # Can be "en" or "ru"
                "prompt_name": "default"
            }
        }

class CombinationResponse(BaseModel):
    element1_id: int
    element2_id: int
    result_id: Optional[int] = None
    result: Optional['Element'] = None
    is_new_discovery: bool
    is_first_discovery: bool = False
    error: Optional[str] = None

class Element(ElementBase):
    id: int
    created_at: datetime
    discovered_by: Optional[Any] = None  # Can be string, list, or None
    language: str = "en"  # "en", "ru", etc.

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# Update forward references
CombinationResponse.model_rebuild()

class ElementList(BaseModel):
    elements: List[Element]

# Player elements schema
class PlayerElementBase(BaseModel):
    element_id: int
    player_name: str

class PlayerElement(PlayerElementBase):
    unlocked_at: datetime
    
    class Config:
        from_attributes = True

class PlayerElementList(BaseModel):
    elements: List[Element]

# Player statistics schemas
class PlayerStatsBase(BaseModel):
    player_name: str

class PlayerStatsCreate(PlayerStatsBase):
    pass

class PlayerStats(PlayerStatsBase):
    id: int
    elements_discovered: int
    elements_unlocked: int
    combinations_tried: int
    successful_combinations: int
    failed_combinations: int
    last_active: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class PlayerStatsList(BaseModel):
    stats: List[PlayerStats]

# Discovery history schemas
class DiscoveryHistoryBase(BaseModel):
    element_id: int
    player_name: str

class DiscoveryHistoryCreate(DiscoveryHistoryBase):
    pass

class DiscoveryHistory(DiscoveryHistoryBase):
    id: int
    discovered_at: datetime
    is_first_discovery: bool
    element: Element

    class Config:
        from_attributes = True

class DiscoveryHistoryList(BaseModel):
    discoveries: List[DiscoveryHistory] 