from pydantic import BaseModel
from typing import List

class ColorResponse(BaseModel):
    """
    Esquema de respuesta para los colores dominantes.
    """
    filename: str
    dominant_colors: List[str]
    message: str
    image_url: str 

class ErrorResponse(BaseModel):
    """
    Esquema de respuesta para errores.
    """
    detail: str