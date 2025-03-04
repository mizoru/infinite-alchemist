from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ElementBase(BaseModel):
    name: str
    emoji: Optional[str] = None
    description: Optional[str] = None
    is_basic: int = 0

class ElementCreate(ElementBase):
    pass

class CombinationRequest(BaseModel):
    element1_id: int
    element2_id: int
    player_name: Optional[str] = None

class CombinationResponse(BaseModel):
    element1_id: int
    element2_id: int
    result_id: int
    result: 'Element'
    is_new_discovery: bool
    is_first_discovery: bool = False

class Element(ElementBase):
    id: int
    created_at: datetime
    discovered_by: Optional[str] = None

    class Config:
        from_attributes = True

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