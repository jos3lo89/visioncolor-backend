import os
import uuid
import logging
from fastapi import (
    APIRouter, 
    UploadFile, 
    File, 
    HTTPException, 
    Depends,
    WebSocket,
    WebSocketDisconnect
)
from sqlmodel import Session
from typing import List

from app.db.database import get_session
from app.db.models import Analysis
from app.services.color_service import get_dominant_colors
from app.api.schemas import ColorResponse, ErrorResponse
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Color Analysis"]
)

@router.post(
    "/analysis/upload",
    response_model=ColorResponse,
    responses={500: {"model": ErrorResponse}}
)
async def upload_image_for_analysis(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Endpoint para subir una imagen (desde galería o cámara).
    Procesa la imagen, extrae colores dominantes y guarda el historial.
    """
    try:
        image_bytes = await file.read()
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        save_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        with open(save_path, "wb") as buffer:
            buffer.write(image_bytes)
        
        logger.info(f"Archivo guardado en: {save_path}")

        dominant_colors = get_dominant_colors(image_bytes, num_colors=5)
        
        analysis_record = Analysis(
            filename=unique_filename,
            dominant_colors=dominant_colors
        )
        session.add(analysis_record)
        session.commit()
        session.refresh(analysis_record)
        
        logger.info(f"Análisis guardado en BBDD: {analysis_record.id}")

        return ColorResponse(
            filename=unique_filename,
            dominant_colors=dominant_colors,
            message="Análisis completado exitosamente."
        )

    except ValueError as e:
        logger.error(f"Error de procesamiento de imagen: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado en upload_image: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

@router.websocket("/analysis/realtime")
async def websocket_realtime_analysis(websocket: WebSocket):
    """
    Endpoint de WebSocket para análisis de color en tiempo real.
    Espera recibir frames de video (como bytes) y devuelve
    los colores dominantes en formato JSON.
    """
    await websocket.accept()
    logger.info("Cliente WebSocket conectado para análisis en tiempo real.")
    
    try:
        while True:
            image_bytes = await websocket.receive_bytes()
            
            try:
                dominant_colors = get_dominant_colors(image_bytes, num_colors=3)
                
                await websocket.send_json({
                    "dominant_colors": dominant_colors
                })
            
            except ValueError as e:
                logger.warning(f"Error procesando frame de WS: {e}")
                await websocket.send_json({"error": str(e)})
            except Exception as e:
                logger.error(f"Error inesperado en WS: {e}")
                await websocket.send_json({"error": f"Error interno: {e}"})

    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado.")
    except Exception as e:
        logger.error(f"Error en la conexión WebSocket: {e}")
        await websocket.close(code=1011) 