from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models.element import DBElement, PlayerStats, player_elements

# Create tables
Base.metadata.create_all(bind=engine)

# Basic elements to initialize
BASIC_ELEMENTS = {
    "en": [
        {"name": "Water", "emoji": "💧", "description": "A clear, colorless liquid essential for life.", "is_basic": True},
        {"name": "Fire", "emoji": "🔥", "description": "The rapid oxidation of material producing heat and light.", "is_basic": True},
        {"name": "Earth", "emoji": "🌍", "description": "The solid ground beneath us and the material that forms it.", "is_basic": True},
        {"name": "Air", "emoji": "💨", "description": "The invisible mixture of gases that surrounds the planet.", "is_basic": True},
    ],
    "ru": [
        {"name": "Вода", "emoji": "💧", "description": "Прозрачная жидкость, необходимая для жизни.", "is_basic": True},
        {"name": "Огонь", "emoji": "🔥", "description": "Быстрое окисление материала, производящее тепло и свет.", "is_basic": True},
        {"name": "Земля", "emoji": "🌍", "description": "Твёрдая поверхность под нами и материал, из которого она состоит.", "is_basic": True},
        {"name": "Воздух", "emoji": "💨", "description": "Невидимая смесь газов, окружающая планету.", "is_basic": True},
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
        
        # Add basic elements for each language
        basic_element_ids = []
        for lang, elements in BASIC_ELEMENTS.items():
            for element_data in elements:
                element = DBElement(**element_data)
                db.add(element)
                db.flush()  # Flush to get the ID
                basic_element_ids.append(element.id)
        
        db.commit()
        print(f"Added {len(basic_element_ids)} basic elements to the database.")
        
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
        basic_elements = db.query(DBElement).filter(DBElement.is_basic == True).all()
        
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