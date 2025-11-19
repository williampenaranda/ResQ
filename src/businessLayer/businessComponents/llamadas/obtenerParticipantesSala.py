"""
Módulo para obtener información de participantes de una sala de LiveKit.
"""

from livekit import api
import logging
from src.businessLayer.businessComponents.llamadas.configLiveKit import get_room_service

logger = logging.getLogger(__name__)


async def obtener_numero_participantes(nombre_sala: str) -> int:
    """
    Obtiene el número de participantes actuales en una sala de LiveKit.

    Args:
        nombre_sala: Nombre de la sala de LiveKit.

    Returns:
        int: Número de participantes en la sala. Retorna 0 si hay error o la sala no existe.

    Raises:
        ValueError: Si el nombre de la sala es inválido.
    """
    if not nombre_sala or not isinstance(nombre_sala, str):
        raise ValueError("El nombre de la sala debe ser una cadena no vacía")

    nombre_sala = nombre_sala.strip()
    if not nombre_sala:
        raise ValueError("El nombre de la sala no puede estar vacío")

    try:
        svc = get_room_service()
        participants_response = await svc.room.list_participants(
            api.ListParticipantsRequest(room=nombre_sala)
        )
        
        if participants_response and hasattr(participants_response, 'participants'):
            return len(participants_response.participants)
        
        return 0
    except Exception as e:
        logger.warning(f"Error al obtener participantes de sala {nombre_sala}: {e}")
        return 0


async def obtener_max_participantes(nombre_sala: str) -> int:
    """
    Obtiene el número máximo de participantes permitidos en una sala.

    Args:
        nombre_sala: Nombre de la sala de LiveKit.

    Returns:
        int: Número máximo de participantes. Retorna 2 por defecto para salas de emergencia.

    Raises:
        ValueError: Si el nombre de la sala es inválido.
    """
    if not nombre_sala or not isinstance(nombre_sala, str):
        raise ValueError("El nombre de la sala debe ser una cadena no vacía")

    nombre_sala = nombre_sala.strip()
    if not nombre_sala:
        raise ValueError("El nombre de la sala no puede estar vacío")

    try:
        svc = get_room_service()
        room_info = await svc.room.list_rooms(api.ListRoomsRequest(names=[nombre_sala]))
        
        if room_info and hasattr(room_info, 'rooms') and room_info.rooms:
            sala = room_info.rooms[0]
            max_participants = getattr(sala, 'max_participants', None)
            if max_participants is not None and max_participants > 0:
                return max_participants
        
        # Valor por defecto para salas de emergencia
        return 2
    except Exception as e:
        logger.warning(f"Error al obtener max_participants de sala {nombre_sala}: {e}")
        # Valor por defecto para salas de emergencia
        return 2


async def verificar_sala_llena(nombre_sala: str) -> bool:
    """
    Verifica si una sala está llena (número de participantes >= máximo permitido).

    Args:
        nombre_sala: Nombre de la sala de LiveKit.

    Returns:
        bool: True si la sala está llena, False en caso contrario.
    """
    try:
        num_participantes = await obtener_numero_participantes(nombre_sala)
        max_participantes = await obtener_max_participantes(nombre_sala)
        return num_participantes >= max_participantes
    except Exception as e:
        logger.warning(f"Error al verificar si sala {nombre_sala} está llena: {e}")
        return False

