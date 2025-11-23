"""
Router para endpoints WebSocket de emergencias.

Este módulo proporciona endpoints WebSocket específicos para comunicación
en tiempo real relacionada con emergencias.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from src.businessLayer.businessComponents.notificaciones.notificadorOperadorEmergencias import get_manager_operadores_emergencia
import json
from typing import Optional

# Obtener el manager de operadores de emergencia desde el módulo de notificación
manager_operadores_emergencia = get_manager_operadores_emergencia()

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket-operadores-emergencia"]
)

@websocket_router.websocket("/operadores-emergencia")
async def websocket_operadores_emergencia(
    websocket: WebSocket,
    id_operador: Optional[int] = Query(None, description="ID del operador de emergencia (opcional)")
):
    """
    Endpoint WebSocket específico para operadores de emergencia.
    
    Permite comunicación en tiempo real relacionada con operadores de emergencia.
    Los operadores se conectan aquí para recibir notificaciones de nuevas solicitudes.
    
    Si se proporciona id_operador, la conexión se asocia a ese ID para recibir
    notificaciones específicas (como información de ambulancias durante la evaluación).
    """
    try:
        # Conectar con el ID del operador si se proporciona
        await manager_operadores_emergencia.connect(websocket, entity_id=id_operador)
        
        # Enviar mensaje de bienvenida
        mensaje_bienvenida = {
            "type": "connection",
            "message": "Conectado! listo para recibir nuevas solicitudes"
        }
        if id_operador:
            mensaje_bienvenida["id_operador"] = id_operador
            mensaje_bienvenida["message"] = f"Conectado como operador {id_operador}! listo para recibir nuevas solicitudes"
        
        await manager_operadores_emergencia.send_personal_message(
            json.dumps(mensaje_bienvenida),
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

