"""
Módulo de configuración compartida para LiveKit.
Centraliza la carga y validación de las variables de entorno de LiveKit.
"""

import os
from dotenv import load_dotenv
from typing import Optional
from livekit import api

# Cargar variables de entorno
load_dotenv()

# Variables de configuración de LiveKit
LIVEKIT_API_KEY: Optional[str] = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET: Optional[str] = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL: Optional[str] = os.getenv("LIVEKIT_URL")

# Instancia global del servicio (singleton pattern)
_room_service: Optional[api.RoomService] = None


def validate_livekit_config() -> None:
    """
    Valida que todas las variables de entorno de LiveKit estén configuradas.
    
    Raises:
        ValueError: Si alguna variable de entorno no está configurada.
    """
    if not LIVEKIT_API_KEY:
        raise ValueError("LIVEKIT_API_KEY no está configurada en las variables de entorno")
    if not LIVEKIT_API_SECRET:
        raise ValueError("LIVEKIT_API_SECRET no está configurada en las variables de entorno")
    if not LIVEKIT_URL:
        raise ValueError("LIVEKIT_URL no está configurada en las variables de entorno")


def get_room_service() -> api.RoomService:
    """
    Obtiene o crea la instancia del servicio de salas de LiveKit.
    Implementa el patrón singleton para reutilizar la conexión.
    
    Returns:
        api.RoomService: Instancia del servicio de salas
        
    Raises:
        ValueError: Si las variables de entorno no están configuradas.
    """
    global _room_service
    
    # Validar configuración antes de crear el servicio
    validate_livekit_config()
    
    if _room_service is None:
        _room_service = api.RoomService(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    
    return _room_service

