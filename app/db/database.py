import logging
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=True, 
)

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def get_session():
    with Session(engine) as session:
        yield session