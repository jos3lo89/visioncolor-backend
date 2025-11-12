from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import router as api_router
from app.db.database import create_db_and_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Función 'lifespan' para manejar eventos de inicio y apagado.
    """
    logger.info("Iniciando aplicación...")
    try:
        create_db_and_tables()
        logger.info("Base de datos y tablas verificadas/creadas.")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise
    
    yield
    
    logger.info("Cerrando aplicación...")

app = FastAPI(
    title="Visión Color API",
    description="API para la detección de colores dominantes en imágenes.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "*",
    # "http://localhost",
    # "http://localhost:3000",
    # "app://.": 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(api_router)

@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "Bienvenido a la API de Visión Color"}