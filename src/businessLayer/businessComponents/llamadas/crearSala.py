"""
Módulo para crear salas de LiveKit.
Proporciona funciones para crear salas personalizadas con configuración específica.
"""

from livekit import api
import logging
from typing import Optional
from src.businessLayer.businessComponents.llamadas.configLiveKit import get_room_service

# Configurar logging
logger = logging.getLogger(__name__)


async def crearSala(nombreSala: str, max_participants: int) -> api.Room:
    """
    Crea una sala de LiveKit con un nombre y un límite de participantes
    específicos, de forma asíncrona.

    Args:
            nombreSala: El nombre único de la sala que se desea crear.
            Debe ser una cadena no vacía y válida para LiveKit.
        max_participants: El número máximo de participantes permitidos.
            Debe ser un entero positivo mayor que 0.

    Returns:
        api.Room: El objeto Room con los detalles de la sala creada.

    Raises:
        ValueError: Si los parámetros de entrada son inválidos.
        RuntimeError: Si hay un error al crear la sala (excepto si ya existe).
        api.exceptions.AlreadyExists: Si la sala ya existe (puede ser manejado opcionalmente).
    """
    # Validación de parámetros de entrada
    if not nombreSala or not isinstance(nombreSala, str):
        raise ValueError("nombreSala debe ser una cadena de texto no vacía")
    
    nombreSala = nombreSala.strip()
    if not nombreSala:
        raise ValueError("nombreSala no puede estar vacío")
    
    if not isinstance(max_participants, int):
        raise ValueError("max_participants debe ser un entero")
    
    if max_participants <= 0:
        raise ValueError("max_participants debe ser mayor que 0")
    
    # Obtener el servicio de salas (singleton)
    svc = get_room_service()
    
    # Definir las opciones de la sala
    options = api.RoomOptions(
        name=nombreSala,
        max_participants=max_participants,
    )
    
    try:
        logger.info(f"Intentando crear sala '{nombreSala}' con máximo {max_participants} participantes")
        
        # Llamar a la API para crear la sala
        room: api.Room = await svc.aroom.create_room(options)
        
        logger.info(f"Sala '{nombreSala}' creada exitosamente. SID: {room.sid}")
        return room
        
    except api.exceptions.AlreadyExists:
        logger.warning(f"La sala '{nombreSala}' ya existe")
        # Opción 1: Relanzar la excepción para que el llamador decida qué hacer
        raise
        # Opción 2: Si quieres obtener la sala existente en lugar de fallar:
        # room = await svc.aroom.get_room(room_name)
        # logger.info(f"Retornando sala existente '{room_name}'. SID: {room.sid}")
        # return room
        
    except api.exceptions.InvalidArgument as e:
        logger.error(f"Argumentos inválidos para crear sala '{nombreSala}': {e}")
        raise ValueError(f"Argumentos inválidos: {e}") from e
        
    except Exception as e:
        logger.error(f"Error inesperado al crear sala '{nombreSala}': {e}", exc_info=True)
        raise RuntimeError(f"Error al crear la sala: {str(e)}") from e


async def obtenerSala(nombreSala: str) -> Optional[api.Room]:
    """
    Obtiene información de una sala existente.
    
    Args:
        nombreSala: El nombre de la sala a buscar.
        
    Returns:
        api.Room si la sala existe, None si no existe.
        
    Raises:
        ValueError: Si nombreSala es inválido.
        RuntimeError: Si hay un error al consultar la sala.
    """
    if not nombreSala or not isinstance(nombreSala, str):
        raise ValueError("nombreSala debe ser una cadena de texto no vacía")
    
    nombreSala = nombreSala.strip()
    if not nombreSala:
        raise ValueError("nombreSala no puede estar vacío")
    
    try:
        svc = get_room_service()
        room = await svc.aroom.get_room(nombreSala)
        return room
    except api.exceptions.NotFound:
        logger.info(f"Sala '{nombreSala}' no encontrada")
        return None
    except Exception as e:
        logger.error(f"Error al obtener sala '{nombreSala}': {e}", exc_info=True)
        raise RuntimeError(f"Error al obtener la sala: {str(e)}") from e
