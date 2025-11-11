"""
Módulo de configuración compartida para LiveKit.
Centraliza la carga y validación de las variables de entorno de LiveKit.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno
load_dotenv()

# Variables de configuración de LiveKit
LIVEKIT_API_KEY: Optional[str] = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET: Optional[str] = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL: Optional[str] = os.getenv("LIVEKIT_URL")

# Instancia global del cliente de API (singleton pattern)
_livekit_api: Optional[object] = None


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


def get_room_service():
    """
    Obtiene o crea la instancia del cliente de API de LiveKit y retorna el servicio de salas.
    Implementa el patrón singleton para reutilizar la conexión.
    
    Returns:
        Instancia del servicio de salas de LiveKit (accesible a través de .aroom)
        
    Raises:
        ValueError: Si las variables de entorno no están configuradas.
    """
    global _livekit_api
    
    # Importar aquí para evitar problemas de carga circular
    from livekit import api
    
    # Validar configuración antes de crear el servicio
    validate_livekit_config()
    
    if _livekit_api is None:
        # Crear el cliente de API de LiveKit
        _livekit_api = api.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )
    
    # Retornar el cliente completo (el servicio de salas está en .aroom)
    return _livekit_api

