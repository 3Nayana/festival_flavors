from sqlalchemy import Column, Integer, String, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session

Base = declarative_base()

# Define the Recipe model
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)              # Username
    festival = Column(String)
    dish = Column(String, nullable=False)
    language = Column(String, nullable=False)
    ingredients = Column(String)
    instructions = Column(String, nullable=False)
    image = Column(LargeBinary)
    latitude = Column(Float)
    longitude = Column(Float)
    video = Column(LargeBinary)
    audio = Column(LargeBinary)

# Database setup (SQLite for local use)
import os

DB_PATH = os.path.join("/tmp", "festival_flavors.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create tables
Base.metadata.create_all(bind=engine)

# Helper to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Save a recipe to the database
def save_recipe(name, festival, dish, language, ingredients, instructions,
                image=None, latitude=None, longitude=None, video=None, audio=None):
    db = SessionLocal()
    new_recipe = Recipe(
        name=name,
        festival=festival,
        dish=dish,
        language=language,
        ingredients=ingredients,
        instructions=instructions,
        image=image,
        latitude=latitude,
        longitude=longitude,
        video=video,
        audio=audio
    )
    db.add(new_recipe)
    db.commit()
    db.close()

# Check if recipe with same name & dish exists
def recipe_exists(name, dish):
    db = SessionLocal()
    exists = db.query(Recipe).filter(Recipe.name == name, Recipe.dish == dish).first()
    db.close()
    return exists is not None

# Search recipes by dish name (case-insensitive)
def search_recipes_by_dish(dish):
    db = SessionLocal()
    results = db.query(Recipe).filter(Recipe.dish.ilike(f"%{dish}%")).all()
    db.close()
    return results
