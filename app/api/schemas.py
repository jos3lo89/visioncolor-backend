from pydantic import BaseModel
from typing import List
from datetime import datetime

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


class AnalysisRead(BaseModel):
    """
    Esquema para LEER un análisis.
    (Usamos un BaseModel para controlar qué datos se envían)
    """
    id: int
    filename: str
    dominant_colors: List[str]
    timestamp: datetime
    image_url: str
    
    class Config:
        from_attributes = True 

class HistoryResponse(BaseModel):
    """
    Esquema de respuesta para la paginación del historial.
    """
    items: List[AnalysisRead]
    total_items: int
    total_pages: int
    current_page: int