# init_db.py

from app.database import Base, engine
from app.recipe_store import Recipe

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
