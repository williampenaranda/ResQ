"""
Módulo para listar salas activas de LiveKit.
Proporciona funciones para obtener información de las salas activas.
"""

from livekit import api
import logging
from typing import List
from src.businessLayer.businessComponents.llamadas.configLiveKit import get_room_service

# Configurar logging
logger = logging.getLogger(__name__)


async def listar_salas_activas() -> List[api.Room]:
    """
    Lista todas las salas activas en LiveKit en ese instante.
    
    Returns:
        List[api.Room]: Lista de objetos Room con los detalles de las salas activas.
        
    Raises:
        RuntimeError: Si hay un error al consultar las salas.
    """
    try:
        svc = get_room_service()
        
        # Solicitar todas las salas activas (sin filtro de nombres)
        response = await svc.room.list_rooms(api.ListRoomsRequest())
        
        logger.info(f"Se encontraron {len(response.rooms)} salas activas")
        return response.rooms
        
    except api.TwirpError as e:
        logger.error(f"Error al listar salas (Twirp {e.code}): {e}", exc_info=True)
        raise RuntimeError(f"Error al listar salas: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error inesperado al listar salas: {e}", exc_info=True)
        raise RuntimeError(f"Error al listar salas: {str(e)}") from e

