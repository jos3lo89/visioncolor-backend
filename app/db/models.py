from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List
from datetime import datetime

class Analysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True) 
    dominant_colors: List[str] = Field(sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    image_url: str = Field(nullable=False) 
    image_public_id: str = Field(nullable=False) 