from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models.element import DBElement, PlayerStats, player_elements

# Create tables
Base.metadata.create_all(bind=engine)

# Language-specific basic elements
LANGUAGE_BASIC_ELEMENTS = {
    "en": [
        {"name": "Water", "emoji": "💧", "is_basic": True, "language": "en"},
        {"name": "Fire", "emoji": "🔥", "is_basic": True, "language": "en"},
        {"name": "Earth", "emoji": "🌍", "is_basic": True, "language": "en"},
        {"name": "Air", "emoji": "💨", "is_basic": True, "language": "en"},
    ],
    "ru": [
        {"name": "Вода", "emoji": "💧", "is_basic": True, "language": "ru"},
        {"name": "Огонь", "emoji": "🔥", "is_basic": True, "language": "ru"},
        {"name": "Земля", "emoji": "🌍", "is_basic": True, "language": "ru"},
        {"name": "Воздух", "emoji": "💨", "is_basic": True, "language": "ru"},
    ]
}

def init_db():
    db = SessionLocal()
    try:
        # Check if we already have elements
        existing_count = db.query(DBElement).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} elements. Skipping initialization.")
            return
        
        # Add language-specific basic elements
        elements_added = 0
        for lang, elements in LANGUAGE_BASIC_ELEMENTS.items():
            for element_data in elements:
                element = DBElement(**element_data)
                db.add(element)
                elements_added += 1
        
        db.commit()
        print(f"Added {elements_added} basic elements across all languages to the database.")
        
        # Make basic elements available to all existing players
        players = db.query(PlayerStats).all()
        for player in players:
            # Get all basic elements
            basic_elements = db.query(DBElement).filter(DBElement.is_basic == True).all()
            
            for element in basic_elements:
                # Add basic elements to player's unlocked elements
                db.execute(
                    player_elements.insert().values(
                        player_name=player.player_name,
                        element_id=element.id
                    )
                )
            # Update player stats
            player.elements_unlocked += len(basic_elements)
        
        db.commit()
        if players:
            print(f"Made basic elements available to {len(players)} existing players.")
    finally:
        db.close()

def add_basic_elements_to_player(player_name: str, language: str = "en"):
    """
    Add basic elements to a new player for the specified language.
    """
    db = SessionLocal()
    try:
        # Get basic elements for the specified language
        basic_elements = db.query(DBElement).filter(
            (DBElement.is_basic == True) & 
            (DBElement.language == language)
        ).all()
        
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