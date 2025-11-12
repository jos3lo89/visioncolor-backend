import logging
import cloudinary
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.db.database import create_db_and_tables
from app.core.config import settings 
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación...")
    
    logger.info("Configurando Cloudinary...")
    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True 
        )
        logger.info("Cloudinary configurado exitosamente.")
    except Exception as e:
        logger.error(f"Error al configurar Cloudinary: {e}")

    logger.info("Verificando la base de datos...")
    try:
        create_db_and_tables()
        logger.info("Tablas de la base de datos verificadas/creadas.")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise e 
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