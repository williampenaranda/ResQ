"""
Endpoints para gestionar salas de LiveKit.
Proporciona endpoints para listar y obtener información de salas activas.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from pydantic import BaseModel, Field
from src.businessLayer.businessComponents.llamadas.listarSalas import listar_salas_activas
from src.businessLayer.businessComponents.llamadas.configLiveKit import get_room_service, LIVEKIT_URL
from livekit import api
from src.api.security import require_auth
import logging

logger = logging.getLogger(__name__)

salas_router = APIRouter(
    prefix="/salas",
    tags=["salas"],
    dependencies=[Depends(require_auth)],
)


class SalaInfo(BaseModel):
    """Modelo de respuesta con información simplificada de una sala."""
    name: str = Field(..., description="Nombre de la sala")
    url: str = Field(..., description="URL del servidor de LiveKit")


class SalasActivasResponse(BaseModel):
    """Modelo de respuesta con la lista de salas activas."""
    total: int = Field(..., description="Total de salas activas")
    salas: List[SalaInfo] = Field(..., description="Lista de salas activas")


@salas_router.get(
    "/activas",
    response_model=SalasActivasResponse,
    summary="Listar salas activas",
    description="Obtiene la lista de salas de emergencia activas que tienen espacio disponible (menos de 2 participantes). Retorna solo el nombre y la URL de cada sala."
)
async def listar_salas_activas_endpoint():
    """
    Endpoint para listar salas de emergencia activas.
    Solo muestra salas que:
    - Son de emergencia (nombre empieza con "emergencia-")
    - Están activas en LiveKit
    - No están llenas (menos de 2 participantes)
    
    Returns:
        SalasActivasResponse: Lista de salas activas con nombre y URL.
    """
    try:
        salas = await listar_salas_activas()
        svc = get_room_service()
        
        # Convertir las salas a modelos de respuesta
        # Filtrar solo salas de emergencia disponibles
        salas_info = []
        for sala in salas:
            # Solo procesar salas de emergencia
            es_sala_emergencia = sala.name.startswith("emergencia-")
            if not es_sala_emergencia:
                continue  # Ignorar salas que no son de emergencia
            
            # Obtener número de participantes usando la API de LiveKit
            num_participants = 0
            try:
                participants_response = await svc.room.list_participants(
                    api.ListParticipantsRequest(room=sala.name)
                )
                if participants_response and hasattr(participants_response, 'participants'):
                    num_participants = len(participants_response.participants)
            except Exception as e:
                logger.warning(f"Error al obtener participantes de sala {sala.name}: {e}")
                # Si no se pueden obtener participantes, intentar usar el atributo directo
                if hasattr(sala, 'num_participants'):
                    num_participants = sala.num_participants
                elif hasattr(sala, 'participants') and sala.participants:
                    num_participants = len(sala.participants)
            
            # Filtrar salas llenas (2 o más participantes)
            if num_participants >= 2:
                continue  # No incluir salas llenas
            
            # Crear información simplificada de la sala
            sala_info = SalaInfo(
                name=sala.name,
                url=LIVEKIT_URL or ""
            )
            salas_info.append(sala_info)
        
        return SalasActivasResponse(
            total=len(salas_info),
            salas=salas_info
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(re)
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar salas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar salas: {str(e)}"
        )

