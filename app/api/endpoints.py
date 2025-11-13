import logging
import math
import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Query, 
    UploadFile, 
    File, 
    HTTPException, 
    Depends,
    WebSocket,
    WebSocketDisconnect
)
from sqlmodel import Session, select, func
from sqlalchemy import desc
from app.db.database import get_session
from app.db.models import Analysis
from app.services.color_service import get_dominant_colors
from app.api.schemas import ColorResponse, ErrorResponse, HistoryResponse

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
    Endpoint para subir una imagen.
    1. La analiza para obtener colores.
    2. La sube a Cloudinary.
    3. Guarda los resultados en la base de datos de Neon.
    """
    try:
        image_bytes = await file.read()

        try:
            logger.info("Subiendo imagen a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                image_bytes,
                folder="visioncolor_uploads", 
                resource_type="image"
            )
            image_url = upload_result["secure_url"]
            public_id = upload_result["public_id"]
            logger.info(f"Imagen subida exitosamente: {image_url}")
            
        except Exception as e:
            logger.error(f"Error al subir a Cloudinary: {e}")
            raise HTTPException(status_code=500, detail=f"Error al guardar la imagen en la nube: {e}")
        
        dominant_colors = get_dominant_colors(image_bytes, num_colors=5)
        
        analysis_record = Analysis(
            filename=file.filename,
            dominant_colors=dominant_colors,
            image_url=image_url,
            image_public_id=public_id
        )
        session.add(analysis_record)
        session.commit()
        session.refresh(analysis_record)
        
        logger.info(f"Análisis guardado en BBDD: {analysis_record.id}")

        return ColorResponse(
            filename=file.filename,
            dominant_colors=dominant_colors,
            message="Análisis completado y guardado en la nube.",
            image_url=image_url
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

@router.get(
    "/analysis/history",
    response_model=HistoryResponse,
    summary="Obtener historial de análisis con paginación"
)
async def get_analysis_history(
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=9, ge=1, le=100, description="Tamaño de la página")
):
    """
    Obtiene una lista paginada de todos los análisis de imágenes
    realizados, ordenados por el más reciente primero.
    """
    try:
        offset = (page - 1) * page_size
        
        statement_items = (
            select(Analysis)
            .order_by(desc(Analysis.timestamp)) 
            .offset(offset)
            .limit(page_size)
        )
        items = session.exec(statement_items).all()
        
        statement_count = select(func.count(Analysis.id))
        total_items = session.exec(statement_count).one()
        
        total_pages = math.ceil(total_items / page_size)
        
        return HistoryResponse(
            items=items, 
            total_items=total_items,
            total_pages=total_pages,
            current_page=page
        )
        
    except Exception as e:
        logger.error(f"Error al obtener el historial: {e}")
        raise HTTPException(status_code=500, detail="Error interno al consultar el historial.")