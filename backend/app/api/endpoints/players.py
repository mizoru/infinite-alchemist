from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.element import PlayerStats
from app.schemas.element import PlayerStats as PlayerStatsSchema, PlayerStatsList, PlayerStatsCreate
from app.db.init_db import add_basic_elements_to_player

router = APIRouter()

@router.get("/", response_model=PlayerStatsList)
def get_player_stats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all player statistics with pagination.
    """
    stats = db.query(PlayerStats).offset(skip).limit(limit).all()
    return {"stats": stats}

@router.get("/{player_name}", response_model=PlayerStatsSchema)
def get_player_stats_by_name(player_name: str, db: Session = Depends(get_db)):
    """
    Get statistics for a specific player by name.
    """
    stats = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
    if stats is None:
        # If player doesn't exist, create a new entry with default values
        stats = PlayerStats(player_name=player_name)
        db.add(stats)
        db.commit()
        db.refresh(stats)
        
        # Add basic elements to the new player
        elements_added = add_basic_elements_to_player(player_name)
        if elements_added > 0:
            # Refresh stats to get updated values
            db.refresh(stats)
    
    return stats

@router.post("/", response_model=PlayerStatsSchema)
def create_player_stats(stats: PlayerStatsCreate, db: Session = Depends(get_db)):
    """
    Create a new player statistics entry.
    """
    # Check if player already exists
    existing_stats = db.query(PlayerStats).filter(PlayerStats.player_name == stats.player_name).first()
    if existing_stats:
        raise HTTPException(status_code=400, detail="Player statistics already exist")
    
    # Create new player stats
    db_stats = PlayerStats(player_name=stats.player_name)
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    
    # Add basic elements to the new player
    add_basic_elements_to_player(stats.player_name)
    
    # Refresh stats to get updated values
    db.refresh(db_stats)
    
    return db_stats

@router.put("/{player_name}/increment", response_model=PlayerStatsSchema)
def increment_player_stats(
    player_name: str, 
    elements_discovered: int = 0, 
    elements_unlocked: int = 0,
    combinations_tried: int = 0,
    successful_combinations: int = 0,
    failed_combinations: int = 0,
    db: Session = Depends(get_db)
):
    """
    Increment player statistics.
    """
    # Get or create player stats
    stats = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
    if stats is None:
        stats = PlayerStats(player_name=player_name)
        db.add(stats)
        db.commit()
        db.refresh(stats)
        
        # Add basic elements to the new player
        add_basic_elements_to_player(player_name)
        
        # Refresh stats to get updated values
        db.refresh(stats)
    
    # Increment stats
    stats.elements_discovered += elements_discovered
    stats.elements_unlocked += elements_unlocked
    stats.combinations_tried += combinations_tried
    stats.successful_combinations += successful_combinations
    stats.failed_combinations += failed_combinations
    
    db.commit()
    db.refresh(stats)
    return stats 