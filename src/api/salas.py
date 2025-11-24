"""
Endpoints para gestionar salas de LiveKit.
Proporciona endpoints para listar y obtener información de salas activas.
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from pydantic import BaseModel, Field
from src.businessLayer.businessComponents.llamadas.listarSalas import listar_salas_activas
from src.businessLayer.businessComponents.llamadas.configLiveKit import get_room_service, LIVEKIT_URL
from src.businessLayer.businessWorkflow.unirseSalaEmergencia import UnirseSalaEmergencia
from livekit import api
import logging

logger = logging.getLogger(__name__)

salas_router = APIRouter(
    prefix="/salas",
    tags=["salas"],
)


class SalaInfo(BaseModel):
    """Modelo de respuesta con información simplificada de una sala."""
    name: str = Field(..., description="Nombre de la sala")
    personas_conectadas: str = Field(..., description="Personas conectadas en formato X/2")


class SalasActivasResponse(BaseModel):
    """Modelo de respuesta con la lista de salas activas."""
    total: int = Field(..., description="Total de salas activas")
    salas: List[SalaInfo] = Field(..., description="Lista de salas activas")


class UnirseSalaRequest(BaseModel):
    """Modelo de request para unirse a una sala."""
    id_operador: int = Field(..., gt=0, description="ID del operador de emergencia")
    room: str = Field(..., min_length=1, description="Nombre de la sala a la que se unirá")


class UnirseSalaResponse(BaseModel):
    """Modelo de respuesta con los datos para entrar a la sala."""
    room: str = Field(..., description="Nombre de la sala")
    token: str = Field(..., description="Token JWT de LiveKit para unirse a la sala")
    identity: str = Field(..., description="Identidad generada para el participante")
    server_url: str = Field(..., description="URL del servidor de LiveKit")


@salas_router.get(
    "/activas",
    response_model=SalasActivasResponse,
    summary="Listar salas activas",
    description="Obtiene la lista de salas de emergencia activas que tienen espacio disponible (menos de 2 participantes). Retorna el nombre y personas conectadas en formato X/2."
)
async def listar_salas_activas_endpoint():
    """
    Endpoint para listar salas de emergencia activas.
    Solo muestra salas que:
    - Son de emergencia (nombre empieza con "emergencia-")
    - Están activas en LiveKit
    - No están llenas (menos de 2 participantes)
    
    Returns:
        SalasActivasResponse: Lista de salas activas con nombre y personas conectadas.
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
            
            # Obtener max_participants de la sala (por defecto 2 para salas de emergencia)
            max_participants = getattr(sala, 'max_participants', None)
            if max_participants is None or max_participants <= 0:
                max_participants = 2  # Valor por defecto para salas de emergencia
            
            # Filtrar salas llenas (2 o más participantes)
            if num_participants >= max_participants:
                continue  # No incluir salas llenas
            
            # Formatear personas conectadas como "X/2"
            personas_conectadas_str = f"{num_participants}/{max_participants}"
            
            # Crear información simplificada de la sala
            sala_info = SalaInfo(
                name=sala.name,
                personas_conectadas=personas_conectadas_str
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


@salas_router.put(
    "",
    response_model=UnirseSalaResponse,
    summary="Unirse a una sala de emergencia",
    description=(
        "Genera las credenciales necesarias (token, identity) para que un operador de emergencia "
        "se una a una sala de LiveKit existente. Retorna los datos necesarios para conectarse a la sala."
    ),
)
async def unirse_a_sala_endpoint(
    request: UnirseSalaRequest = Body(
        ...,
        examples={
            "ejemploBasico": {
                "summary": "Unirse a sala",
                "value": {
                    "id_operador": 1,
                    "room": "emergencia-uuid-1234"
                }
            }
        }
    )
) -> UnirseSalaResponse:
    """
    Endpoint para que un operador de emergencia se una a una sala existente.
    
    Recibe el ID del operador y el nombre de la sala, y retorna:
    - room: Nombre de la sala
    - token: Token JWT para acceder a la sala
    - identity: Identidad del participante
    - server_url: URL del servidor de LiveKit
    
    Returns:
        UnirseSalaResponse: Datos necesarios para conectarse a la sala.
    """
    try:
        result = await UnirseSalaEmergencia.unirse_a_sala(
            id_operador=request.id_operador,
            nombre_sala=request.room
        )
        return UnirseSalaResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error inesperado al unirse a la sala: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al unirse a la sala: {str(e)}"
        )

