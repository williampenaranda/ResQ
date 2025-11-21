"""
Router para endpoints WebSocket de emergencias.

Este módulo proporciona endpoints WebSocket específicos para comunicación
en tiempo real relacionada con emergencias.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.businessLayer.businessComponents.notificaciones.notificadorOperadorEmergencias import get_manager_operadores_emergencia
import json

# Obtener el manager de operadores de emergencia desde el módulo de notificación
manager_operadores_emergencia = get_manager_operadores_emergencia()

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket-operadores-emergencia"]
)

@websocket_router.websocket("/operadores-emergencia")
async def websocket_operadores_emergencia(websocket: WebSocket):
    """
    Endpoint WebSocket específico para operadores de emergencia.
    
    Permite comunicación en tiempo real relacionada con operadores de emergencia.
    Los operadores se conectan aquí para recibir notificaciones de nuevas solicitudes.
    """
    try:
        await manager_operadores_emergencia.connect(websocket)
        
        # Enviar mensaje de bienvenida
        await manager_operadores_emergencia.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Conectado! listo para recibir nuevas solicitudes"
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
        manager_operadores_emergencia.disconnect(websocket)
    except Exception as e:
        # Log del error para debugging
        print(f"Error en websocket de operadores de emergencia: {e}")
        try:
            manager_operadores_emergencia.disconnect(websocket)
        except:
            pass

