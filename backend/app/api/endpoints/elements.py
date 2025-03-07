from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.element import DBElement, element_combinations, PlayerStats, DiscoveryHistory, player_elements
from app.schemas.element import ElementCreate, Element as ElementSchema, ElementList, CombinationRequest, CombinationResponse, PlayerElementList
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

@router.get("/", response_model=ElementList)
def get_elements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all elements with pagination.
    """
    elements = db.query(DBElement).offset(skip).limit(limit).all()
    
    # Convert elements to dictionaries to handle the discovered_by relationship
    element_dicts = []
    for element in elements:
        element_dict = {
            "id": element.id,
            "name": element.name,
            "emoji": element.emoji,
            "description": element.description,
            "is_basic": element.is_basic,
            "created_at": element.created_at,
            "discovered_by": None  # Set discovered_by to None for now
        }
        element_dicts.append(element_dict)
    
    return {"elements": element_dicts}

@router.get("/player/{player_name}", response_model=PlayerElementList)
def get_player_elements(player_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all elements unlocked by a specific player.
    """
    # Get player stats or create if not exists
    player = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
    if not player:
        player = PlayerStats(player_name=player_name)
        db.add(player)
        db.commit()
        db.refresh(player)
    
    # Get all elements unlocked by the player
    elements = db.query(DBElement).join(
        player_elements, 
        DBElement.id == player_elements.c.element_id
    ).filter(
        player_elements.c.player_name == player_name
    ).offset(skip).limit(limit).all()
    
    # Convert elements to dictionaries to handle the discovered_by relationship
    element_dicts = []
    for element in elements:
        element_dict = {
            "id": element.id,
            "name": element.name,
            "emoji": element.emoji,
            "description": element.description,
            "is_basic": element.is_basic,
            "created_at": element.created_at,
            "discovered_by": None  # Set discovered_by to None for now
        }
        element_dicts.append(element_dict)
    
    return {"elements": element_dicts}

@router.get("/{element_id}", response_model=ElementSchema)
def get_element(element_id: int, db: Session = Depends(get_db)):
    """
    Get a specific element by ID.
    """
    element = db.query(DBElement).filter(DBElement.id == element_id).first()
    if element is None:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Convert element to dictionary to handle the discovered_by relationship
    element_dict = {
        "id": element.id,
        "name": element.name,
        "emoji": element.emoji,
        "description": element.description,
        "is_basic": element.is_basic,
        "created_at": element.created_at,
        "discovered_by": None  # Set discovered_by to None for now
    }
    
    return element_dict

@router.post("/", response_model=ElementSchema)
def create_element(element: ElementCreate, db: Session = Depends(get_db)):
    """
    Create a new element.
    """
    db_element = DBElement(
        name=element.name,
        emoji=element.emoji,
        description=element.description,
        is_basic=element.is_basic
    )
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element

@router.post("/combine", response_model=CombinationResponse)
def combine_elements(combination: CombinationRequest, db: Session = Depends(get_db)):
    """
    Combine two elements to create a new one or get an existing combination.
    """
    # Get the elements from the database
    element1 = db.query(DBElement).filter(DBElement.id == combination.element1_id).first()
    element2 = db.query(DBElement).filter(DBElement.id == combination.element2_id).first()
    
    if not element1 or not element2:
        raise HTTPException(status_code=404, detail="One or both elements not found")
    
    # Update player statistics for combination attempt
    if combination.player_name:
        update_player_stats(db, combination.player_name, combinations_tried=1)
    
    # Check if this combination already exists
    existing_combination = db.execute(
        element_combinations.select().where(
            (element_combinations.c.element1_id == combination.element1_id) &
            (element_combinations.c.element2_id == combination.element2_id)
        )
    ).first()
    
    # If the combination exists, return the result
    if existing_combination:
        result_element = db.query(DBElement).filter(DBElement.id == existing_combination.result_id).first()
        
        # Check if this is a new unlock for the player
        is_new_unlock = False
        if combination.player_name:
            is_new_unlock = unlock_element_for_player(db, combination.player_name, result_element.id)
            update_player_stats(db, combination.player_name, successful_combinations=1)
            if is_new_unlock:
                update_player_stats(db, combination.player_name, elements_unlocked=1)
            
        return {
            "element1_id": combination.element1_id,
            "element2_id": combination.element2_id,
            "result_id": result_element.id,
            "result": {
                "id": result_element.id,
                "name": result_element.name,
                "emoji": result_element.emoji,
                "description": "",
                "is_basic": result_element.is_basic,
                "created_at": result_element.created_at,
                "discovered_by": None  # Set discovered_by to None for now
            },
            "is_new_discovery": False,
            "is_first_discovery": False
        }
    
    # If the combination doesn't exist, use the LLM to determine the result
    llm_result = llm_service.combine_elements(element1.name, element2.name)
    
    # Check if the resulting element already exists
    result_element = db.query(DBElement).filter(DBElement.name == llm_result["result"]).first()
    is_new_discovery = False
    is_first_discovery = False
    
    # If the resulting element doesn't exist, create it
    if not result_element:
        result_element = DBElement(
            name=llm_result["result"],
            emoji=llm_result["emoji"],
            description="",
            discovered_by=combination.player_name
        )
        db.add(result_element)
        db.commit()
        db.refresh(result_element)
        is_new_discovery = True
        is_first_discovery = True
        
        # Record the discovery in history
        if combination.player_name:
            record_discovery(db, result_element.id, combination.player_name, is_first_discovery=True)
            # Update player statistics for new element discovery
            update_player_stats(db, combination.player_name, elements_discovered=1, elements_unlocked=1, successful_combinations=1)
            # Unlock the element for the player
            unlock_element_for_player(db, combination.player_name, result_element.id)
    else:
        # Element exists but might be new to this player
        is_new_unlock = False
        if combination.player_name:
            is_new_unlock = unlock_element_for_player(db, combination.player_name, result_element.id)
            record_discovery(db, result_element.id, combination.player_name, is_first_discovery=False)
            # Update player statistics
            update_player_stats(db, combination.player_name, successful_combinations=1)
            if is_new_unlock:
                update_player_stats(db, combination.player_name, elements_unlocked=1)
    
    # Create the combination record
    db.execute(
        element_combinations.insert().values(
            element1_id=combination.element1_id,
            element2_id=combination.element2_id,
            result_id=result_element.id,
            discovered_by=combination.player_name
        )
    )
    db.commit()
    
    # Return the combination result
    return {
        "element1_id": combination.element1_id,
        "element2_id": combination.element2_id,
        "result_id": result_element.id,
        "result": {
            "id": result_element.id,
            "name": result_element.name,
            "emoji": result_element.emoji,
            "description": "",
            "is_basic": result_element.is_basic,
            "created_at": result_element.created_at,
            "discovered_by": None  # Set discovered_by to None for now
        },
        "is_new_discovery": is_new_discovery,
        "is_first_discovery": is_first_discovery
    }

def update_player_stats(db: Session, player_name: str, **kwargs):
    """
    Update player statistics.
    """
    if not player_name:
        return
        
    # Get or create player stats
    stats = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
    if not stats:
        stats = PlayerStats(player_name=player_name)
        db.add(stats)
    
    # Update stats
    for key, value in kwargs.items():
        if hasattr(stats, key):
            setattr(stats, key, getattr(stats, key) + value)
    
    db.commit()

def record_discovery(db: Session, element_id: int, player_name: str, is_first_discovery: bool = False):
    """
    Record a new element discovery in the history.
    """
    if not player_name:
        return
        
    discovery = DiscoveryHistory(
        element_id=element_id,
        player_name=player_name,
        is_first_discovery=is_first_discovery
    )
    db.add(discovery)
    db.commit()

def unlock_element_for_player(db: Session, player_name: str, element_id: int) -> bool:
    """
    Unlock an element for a player. Returns True if this is a new unlock.
    """
    if not player_name:
        return False
        
    # Check if the player already has this element
    existing = db.execute(
        player_elements.select().where(
            (player_elements.c.player_name == player_name) &
            (player_elements.c.element_id == element_id)
        )
    ).first()
    
    if existing:
        return False
        
    # Add the element to the player's unlocked elements
    db.execute(
        player_elements.insert().values(
            player_name=player_name,
            element_id=element_id
        )
    )
    db.commit()
    
    return True 