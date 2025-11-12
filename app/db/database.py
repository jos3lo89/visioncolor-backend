from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings
import logging

connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    """
    Crea la base de datos y las tablas si no existen.
    """
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def get_session():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.
    """
    with Session(engine) as session:
        yield session