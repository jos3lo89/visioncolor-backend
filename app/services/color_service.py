import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import io
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_dominant_colors(image_bytes: bytes, num_colors: int = 5) -> List[str]:
    """
    Extrae los colores dominantes de una imagen usando K-Means.
    
    :param image_bytes: Bytes de la imagen
    :param num_colors: Número de colores dominantes a extraer
    :return: Lista de colores en formato hexadecimal
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        image = image.convert("RGB")
        
        image.thumbnail((150, 150))
        
        np_image = np.array(image)
        pixels = np_image.reshape((-1, 3))
        
        kmeans = KMeans(n_clusters=num_colors, n_init='auto', random_state=42)
        kmeans.fit(pixels)
        
        dominant_colors_rgb = kmeans.cluster_centers_.astype(int)
        
        hex_colors = []
        for color in dominant_colors_rgb:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            hex_colors.append(hex_color)
            
        logger.info(f"Colores dominantes extraídos: {hex_colors}")
        return hex_colors

    except Image.DecompressionBombError:
        logger.error("Error: La imagen es demasiado grande (Decompression Bomb).")
        raise ValueError("La imagen es demasiado grande para procesar.")
    except Exception as e:
        logger.error(f"Error procesando la imagen: {e}")
        raise ValueError(f"Error interno al procesar la imagen: {e}")