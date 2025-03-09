from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.db.database import SessionLocal, Base, engine
from app.models.element import DBElement, element_combinations
import os

def migrate_db():
    """
    Migrate the database to support language-specific elements.
    
    This script:
    1. Adds language and universal_id columns to the elements table
    2. Adds language column to the element_combinations table
    3. Updates existing elements to set appropriate language values
    4. Creates language-specific variants of basic elements
    5. Removes the unique constraint on name and adds a unique constraint on (name, language)
    """
    db = SessionLocal()
    try:
        print("Starting database migration...")
        
        # Check if migration is needed
        # Try to query for the language column to see if it exists
        try:
            db.query(DBElement.language).first()
            print("Migration already applied. Skipping.")
            return
        except:
            print("Language column not found. Proceeding with migration.")
        
        # Add language and universal_id columns to elements table
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE elements ADD COLUMN language VARCHAR DEFAULT 'universal'"))
            conn.execute(text("ALTER TABLE elements ADD COLUMN universal_id INTEGER REFERENCES elements(id)"))
            
            # Add language column to element_combinations table
            conn.execute(text("ALTER TABLE element_combinations ADD COLUMN language VARCHAR DEFAULT 'en'"))
            
            # Update existing elements to set language to 'en' (default)
            conn.execute(text("UPDATE elements SET language = 'en'"))
            
            # Remove the unique constraint on name
            # This is tricky in SQLite as it doesn't support DROP CONSTRAINT
            # We need to recreate the table without the unique constraint
            
            # First, create a new table without the unique constraint
            conn.execute(text("""
                CREATE TABLE elements_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    emoji VARCHAR DEFAULT '✨',
                    is_basic BOOLEAN DEFAULT 0,
                    language VARCHAR DEFAULT 'universal',
                    universal_id INTEGER REFERENCES elements(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR
                )
            """))
            
            # Copy data from the old table to the new one
            conn.execute(text("""
                INSERT INTO elements_new 
                SELECT id, name, emoji, is_basic, language, universal_id, created_at, created_by 
                FROM elements
            """))
            
            # Drop the old table
            conn.execute(text("DROP TABLE elements"))
            
            # Rename the new table to the original name
            conn.execute(text("ALTER TABLE elements_new RENAME TO elements"))
            
            # Create indexes
            conn.execute(text("CREATE INDEX ix_elements_name ON elements (name)"))
            conn.execute(text("CREATE INDEX ix_elements_language ON elements (language)"))
            
            # Create a unique index on the combination of name and language
            conn.execute(text("CREATE UNIQUE INDEX ix_elements_name_language ON elements (name, language)"))
            
            conn.commit()
        
        # Get all basic elements
        basic_elements = db.query(DBElement).filter(DBElement.is_basic == True).all()
        
        # Create Russian variants of basic elements
        en_to_ru = {
            "Water": "Вода",
            "Fire": "Огонь",
            "Earth": "Земля",
            "Air": "Воздух"
        }
        
        # Update basic elements to be universal
        for element in basic_elements:
            if element.name in en_to_ru:
                # Set language to universal
                element.language = "universal"
                db.add(element)
                
                # Create Russian variant
                ru_element = DBElement(
                    name=en_to_ru[element.name],
                    emoji=element.emoji,
                    is_basic=True,
                    language="ru",
                    universal_id=element.id
                )
                db.add(ru_element)
        
        db.commit()
        print("Migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_db() 