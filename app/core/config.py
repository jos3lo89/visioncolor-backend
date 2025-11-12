from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    """
    DATABASE_URL: str
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"

settings = Settings()