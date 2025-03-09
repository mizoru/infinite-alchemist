from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models.element import DBElement, PlayerStats, player_elements

# Create tables
Base.metadata.create_all(bind=engine)

# Universal basic elements
UNIVERSAL_BASIC_ELEMENTS = [
    {"name": "Water", "emoji": "💧", "description": "A clear, colorless liquid essential for life.", "is_basic": True, "language": "universal"},
    {"name": "Fire", "emoji": "🔥", "description": "The rapid oxidation of material producing heat and light.", "is_basic": True, "language": "universal"},
    {"name": "Earth", "emoji": "🌍", "description": "The solid ground beneath us and the material that forms it.", "is_basic": True, "language": "universal"},
    {"name": "Air", "emoji": "💨", "description": "The invisible mixture of gases that surrounds the planet.", "is_basic": True, "language": "universal"},
]

# Language-specific names for basic elements
LANGUAGE_BASIC_ELEMENTS = {
    "en": [
        {"name": "Water", "emoji": "💧", "description": "A clear, colorless liquid essential for life."},
        {"name": "Fire", "emoji": "🔥", "description": "The rapid oxidation of material producing heat and light."},
        {"name": "Earth", "emoji": "🌍", "description": "The solid ground beneath us and the material that forms it."},
        {"name": "Air", "emoji": "💨", "description": "The invisible mixture of gases that surrounds the planet."},
    ],
    "ru": [
        {"name": "Вода", "emoji": "💧", "description": "Прозрачная жидкость, необходимая для жизни."},
        {"name": "Огонь", "emoji": "🔥", "description": "Быстрое окисление материала, производящее тепло и свет."},
        {"name": "Земля", "emoji": "🌍", "description": "Твёрдая поверхность под нами и материал, из которого она состоит."},
        {"name": "Воздух", "emoji": "💨", "description": "Невидимая смесь газов, окружающая планету."},
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
        
        # Add universal basic elements first
        universal_elements = {}
        for element_data in UNIVERSAL_BASIC_ELEMENTS:
            element = DBElement(**element_data)
            db.add(element)
            db.flush()  # Flush to get the ID
            universal_elements[element.name] = element.id
        
        # Add language-specific variants of basic elements
        for lang, elements in LANGUAGE_BASIC_ELEMENTS.items():
            for i, element_data in enumerate(elements):
                # Get the corresponding universal element
                universal_name = UNIVERSAL_BASIC_ELEMENTS[i]["name"]
                universal_id = universal_elements[universal_name]
                
                # Create language-specific element
                element = DBElement(
                    name=element_data["name"],
                    emoji=element_data["emoji"],
                    description=element_data["description"],
                    is_basic=True,
                    language=lang,
                    universal_id=universal_id
                )
                db.add(element)
        
        db.commit()
        print(f"Added {len(universal_elements)} universal basic elements and their language variants to the database.")
        
        # Make basic elements available to all existing players
        players = db.query(PlayerStats).all()
        for player in players:
            # Get all basic elements (both universal and language-specific)
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