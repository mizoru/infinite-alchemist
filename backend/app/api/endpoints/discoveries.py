from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.element import DiscoveryHistory, Element, player_elements
from app.schemas.element import DiscoveryHistory as DiscoveryHistorySchema
from app.schemas.element import DiscoveryHistoryList, DiscoveryHistoryCreate

router = APIRouter()

@router.get("/", response_model=DiscoveryHistoryList)
def get_discoveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all element discoveries with pagination.
    """
    discoveries = db.query(DiscoveryHistory).order_by(DiscoveryHistory.discovered_at.desc()).offset(skip).limit(limit).all()
    return {"discoveries": discoveries}

@router.get("/first", response_model=DiscoveryHistoryList)
def get_first_discoveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all first discoveries (elements that were discovered for the first time).
    """
    discoveries = db.query(DiscoveryHistory).filter(
        DiscoveryHistory.is_first_discovery == True
    ).order_by(DiscoveryHistory.discovered_at.desc()).offset(skip).limit(limit).all()
    
    return {"discoveries": discoveries}

@router.get("/player/{player_name}", response_model=DiscoveryHistoryList)
def get_player_discoveries(player_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all discoveries by a specific player.
    """
    discoveries = db.query(DiscoveryHistory).filter(
        DiscoveryHistory.player_name == player_name
    ).order_by(DiscoveryHistory.discovered_at.desc()).offset(skip).limit(limit).all()
    
    return {"discoveries": discoveries}

@router.get("/player/{player_name}/first", response_model=DiscoveryHistoryList)
def get_player_first_discoveries(player_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all first discoveries by a specific player (elements they discovered first).
    """
    discoveries = db.query(DiscoveryHistory).filter(
        DiscoveryHistory.player_name == player_name,
        DiscoveryHistory.is_first_discovery == True
    ).order_by(DiscoveryHistory.discovered_at.desc()).offset(skip).limit(limit).all()
    
    return {"discoveries": discoveries}

@router.get("/element/{element_id}", response_model=DiscoveryHistoryList)
def get_element_discoveries(element_id: int, db: Session = Depends(get_db)):
    """
    Get discovery history for a specific element.
    """
    # Check if element exists
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    discoveries = db.query(DiscoveryHistory).filter(
        DiscoveryHistory.element_id == element_id
    ).order_by(DiscoveryHistory.discovered_at.desc()).all()
    
    return {"discoveries": discoveries}

@router.get("/element/{element_id}/first", response_model=DiscoveryHistorySchema)
def get_element_first_discovery(element_id: int, db: Session = Depends(get_db)):
    """
    Get the first discovery of a specific element.
    """
    # Check if element exists
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    discovery = db.query(DiscoveryHistory).filter(
        DiscoveryHistory.element_id == element_id,
        DiscoveryHistory.is_first_discovery == True
    ).first()
    
    if not discovery:
        raise HTTPException(status_code=404, detail="No first discovery record found for this element")
    
    return discovery

@router.post("/", response_model=DiscoveryHistorySchema)
def create_discovery(discovery: DiscoveryHistoryCreate, db: Session = Depends(get_db)):
    """
    Record a new element discovery.
    """
    # Check if element exists
    element = db.query(Element).filter(Element.id == discovery.element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Check if this is the first discovery of this element
    is_first = not db.query(DiscoveryHistory).filter(
        DiscoveryHistory.element_id == discovery.element_id,
        DiscoveryHistory.is_first_discovery == True
    ).first()
    
    # Create discovery record
    db_discovery = DiscoveryHistory(
        element_id=discovery.element_id,
        player_name=discovery.player_name,
        is_first_discovery=is_first
    )
    db.add(db_discovery)
    
    # If this is the first discovery, update the element
    if is_first:
        pass
        
    db.commit()
    db.refresh(db_discovery)
    
    return db_discovery 