from sqlalchemy import text
from model.database import engine

def migrate():
    with engine.begin() as conn:
        try:
            print("Starting migration...")
            conn.execute(text("ALTER TABLE users ALTER COLUMN phone_number TYPE VARCHAR(100)"))
            conn.execute(text("ALTER TABLE registration_sessions ALTER COLUMN phone_number TYPE VARCHAR(100)"))
            
            # Verify the change
            result = conn.execute(text("SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'registration_sessions' AND column_name = 'phone_number'"))
            print(f"Verification: {result.fetchone()}")
            
            print("Migration successful: Updated phone_number columns to VARCHAR(100)")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
