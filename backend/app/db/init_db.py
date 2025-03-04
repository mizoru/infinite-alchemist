from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models.element import Element, PlayerStats, player_elements

# Create tables
Base.metadata.create_all(bind=engine)

# Basic elements to initialize
BASIC_ELEMENTS = [
    {"name": "Water", "emoji": "💧", "description": "A clear, colorless liquid essential for life.", "is_basic": 1},
    {"name": "Fire", "emoji": "🔥", "description": "The rapid oxidation of material producing heat and light.", "is_basic": 1},
    {"name": "Earth", "emoji": "🌍", "description": "The solid ground beneath us and the material that forms it.", "is_basic": 1},
    {"name": "Air", "emoji": "💨", "description": "The invisible mixture of gases that surrounds the planet.", "is_basic": 1},
]

def init_db():
    db = SessionLocal()
    try:
        # Check if we already have elements
        existing_count = db.query(Element).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} elements. Skipping initialization.")
            return
        
        # Add basic elements
        basic_element_ids = []
        for element_data in BASIC_ELEMENTS:
            element = Element(**element_data)
            db.add(element)
            db.flush()  # Flush to get the ID
            basic_element_ids.append(element.id)
        
        db.commit()
        print(f"Added {len(BASIC_ELEMENTS)} basic elements to the database.")
        
        # Make basic elements available to all existing players
        players = db.query(PlayerStats).all()
        for player in players:
            for element_id in basic_element_ids:
                # Add basic elements to player's unlocked elements
                db.execute(
                    player_elements.insert().values(
                        player_name=player.player_name,
                        element_id=element_id
                    )
                )
            # Update player stats
            player.elements_unlocked += len(basic_element_ids)
        
        db.commit()
        if players:
            print(f"Made basic elements available to {len(players)} existing players.")
    finally:
        db.close()

def add_basic_elements_to_player(player_name: str):
    """
    Add basic elements to a new player.
    """
    db = SessionLocal()
    try:
        # Get basic elements
        basic_elements = db.query(Element).filter(Element.is_basic == 1).all()
        
        # Get or create player
        player = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
        if not player:
            player = PlayerStats(player_name=player_name)
            db.add(player)
            db.flush()
        
        # Add basic elements to player's unlocked elements
        elements_added = 0
        for element in basic_elements:
            # Check if player already has this element
            existing = db.execute(
                player_elements.select().where(
                    (player_elements.c.player_name == player_name) &
                    (player_elements.c.element_id == element.id)
                )
            ).first()
            
            if not existing:
                db.execute(
                    player_elements.insert().values(
                        player_name=player_name,
                        element_id=element.id
                    )
                )
                elements_added += 1
        
        # Update player stats
        if elements_added > 0:
            player.elements_unlocked += elements_added
        
        db.commit()
        return elements_added
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 