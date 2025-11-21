"""
Componente de comunicación para notificar eventos relacionados con emergencias
a través del WebSocket de operadores de emergencia.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from src.comunication.conexionWebsocket import ConnectionManager

# Manager específico para operadores de emergencia
manager_operadores_emergencia = ConnectionManager()


async def notificar_nueva_solicitud(nombre_sala: str, datos_solicitud: Dict[str, Any]):
    """
    Notifica a todos los clientes conectados al WebSocket de emergencias
    sobre una nueva solicitud recibida, incluyendo el nombre de la sala.

    Args:
        nombre_sala: Nombre de la sala creada para la emergencia.
        datos_solicitud: Diccionario con la información de la solicitud.
    """
    message = json.dumps({
        "type": "nueva_solicitud",
        "data": {
            **datos_solicitud,
            "room": nombre_sala
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Broadcast a todos los conectados al endpoint de emergencias
    await manager_operadores_emergencia.broadcast(message)


async def notificar_sala_atendida(nombre_sala: str):
    """
    Notifica a todos los clientes conectados al WebSocket de emergencias
    que una sala ha sido atendida (está llena con 2 participantes).

    Args:
        nombre_sala: Nombre de la sala que ha sido atendida.
    """
    message = json.dumps({
        "type": "sala_atendida",
        "data": {
            "room": nombre_sala,
            "estado": "atendida"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Broadcast a todos los conectados al endpoint de emergencias
    await manager_operadores_emergencia.broadcast(message)


def get_manager_operadores_emergencia() -> ConnectionManager:
    """
    Obtiene el manager de conexiones de operadores de emergencia.
    
    Returns:
        ConnectionManager: Instancia del manager de conexiones de operadores de emergencia.
    """
    return manager_operadores_emergencia

