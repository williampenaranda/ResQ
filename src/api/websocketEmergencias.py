"""
Router para endpoints WebSocket de emergencias.

Este módulo proporciona endpoints WebSocket específicos para comunicación
en tiempo real relacionada con emergencias.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.comunication.notificadorEmergencias import get_manager_emergencias
import json

# Obtener el manager de emergencias desde el módulo de notificación
manager_emergencias = get_manager_emergencias()

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket-emergencias"]
)

@websocket_router.websocket("/emergencias")
async def websocket_emergencia(websocket: WebSocket):
    """
    Endpoint WebSocket específico para emergencias.
    
    Permite comunicación en tiempo real relacionada con emergencias.
    Los operadores se conectan aquí para recibir notificaciones de:
    - Nuevas solicitudes de ambulancia (tipo: "nueva_solicitud")
    - Salas atendidas (tipo: "sala_atendida")
    
    Mensajes enviados:
    - "nueva_solicitud": Cuando se crea una nueva solicitud de ambulancia
      - data.room: Nombre de la sala creada
      - data: Información completa de la solicitud
    - "sala_atendida": Cuando una sala se llena (2 participantes)
      - data.room: Nombre de la sala atendida
      - data.estado: "atendida"
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

