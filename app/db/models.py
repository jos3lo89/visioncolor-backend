from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List
from datetime import datetime

class Analysis(SQLModel, table=True):
    """
    Modelo de tabla para el historial de análisis de color.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    dominant_colors: List[str] = Field(sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)