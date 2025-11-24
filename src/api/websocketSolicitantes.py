"""
Router para endpoints WebSocket de solicitantes.

Este módulo proporciona endpoints WebSocket específicos para comunicación
en tiempo real relacionada con solicitantes y sus solicitudes.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Path
from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import get_manager_solicitantes
import json

# Obtener el manager de solicitantes desde el módulo de notificación
manager_solicitantes = get_manager_solicitantes()

websocket_solicitantes_router = APIRouter(
    prefix="/ws",
    tags=["websocket-solicitantes"]
)

@websocket_solicitantes_router.websocket("/solicitantes/{id_solicitante}")
async def websocket_solicitante(
    websocket: WebSocket,
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante")
):
    """
    Endpoint WebSocket específico para solicitantes.
    
    Permite comunicación en tiempo real relacionada con solicitantes.
    Los solicitantes se conectan aquí usando su ID para recibir notificaciones
    sobre el estado de sus solicitudes.
    
    Args:
        websocket: Conexión WebSocket.
        id_solicitante: ID del solicitante que se conecta.
    """
    try:
        # Conectar el websocket asociado al ID del solicitante
        await manager_solicitantes.connect(websocket, entity_id=id_solicitante)
        
        # Enviar mensaje de bienvenida
        await manager_solicitantes.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": f"Conectado como solicitante {id_solicitante}! Listo para recibir actualizaciones de tu solicitud",
                "id_solicitante": id_solicitante
            }),
            websocket
        )
        
        # Mantener la conexión activa escuchando mensajes
        while True:
            # Recibir mensajes del cliente (pueden ser pings o comandos)
            try:
                data = await websocket.receive_text()
                # Opcional: procesar mensajes del cliente si es necesario
                
            except Exception:
                break
        
        # Si salimos del bucle, desconectar y detener tareas
        manager_solicitantes.disconnect(websocket)
        from src.businessLayer.businessComponents.notificaciones.gestorTareasUbicacionAmbulancia import detener_envio_por_solicitante
        detener_envio_por_solicitante(id_solicitante)
                
    except WebSocketDisconnect:
        manager_solicitantes.disconnect(websocket)
        # Verificar si hay tareas de envío de ubicación activas para este solicitante y detenerlas
        from src.businessLayer.businessComponents.notificaciones.gestorTareasUbicacionAmbulancia import detener_envio_por_solicitante
        detener_envio_por_solicitante(id_solicitante)
    except Exception as e:
        # Log del error para debugging
        print(f"Error en websocket de solicitante {id_solicitante}: {e}")
        try:
            manager_solicitantes.disconnect(websocket)
            # Verificar si hay tareas de envío de ubicación activas para este solicitante y detenerlas
            from src.businessLayer.businessComponents.notificaciones.gestorTareasUbicacionAmbulancia import detener_envio_por_solicitante
            detener_envio_por_solicitante(id_solicitante)
        except:
            pass

