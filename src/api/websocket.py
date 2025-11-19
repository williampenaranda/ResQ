"""
Router para endpoints WebSocket.

Este módulo proporciona endpoints WebSocket para comunicación en tiempo real.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.comunication.conexionWebsocket import ConnectionManager
import json
from datetime import datetime, timezone
from src.businessLayer.businessEntities.solicitud import Solicitud

# Crear instancias del ConnectionManager
# Manager general para el endpoint básico
manager = ConnectionManager()

# Manager específico para emergencias
manager_emergencias = ConnectionManager()


async def notificar_nueva_solicitud(solicitud: Solicitud | dict):
    """
    Notifica a todos los clientes conectados al WebSocket de emergencias
    sobre una nueva solicitud recibida.
    
    Args:
        solicitud_data: Diccionario con la información de la solicitud
    """
    if isinstance(solicitud, Solicitud):
        data = solicitud.model_dump()
    elif hasattr(solicitud, "model_dump"):
        data = solicitud.model_dump()
    else:
        data = solicitud

    message = json.dumps({
        "type": "nueva_solicitud",
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Broadcast a todos los conectados al endpoint de emergencias
    await manager_emergencias.broadcast(message)

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

@websocket_router.websocket("/emergencias")
async def websocket_emergencia(websocket: WebSocket):
    """
    Endpoint WebSocket específico para emergencias.
    
    Permite comunicación en tiempo real relacionada con emergencias.
    Los operadores se conectan aquí para recibir notificaciones de nuevas solicitudes.
    """
    await manager_emergencias.connect(websocket)
    try:
        # Enviar mensaje de bienvenida
        await manager_emergencias.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Conectado! listo para recibir emergencias"
            }),
            websocket
        )
        
        # Mantener la conexión activa escuchando mensajes
        while True:
            # Recibir mensajes del cliente (pueden ser pings o comandos)
            try:
                data = await websocket.receive_text()
                
            except Exception:
                break
                
    except WebSocketDisconnect:
        manager_emergencias.disconnect(websocket)

