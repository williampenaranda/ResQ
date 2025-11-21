"""
Router para endpoints WebSocket de ambulancias.

Este módulo proporciona endpoints WebSocket específicos para comunicación
en tiempo real relacionada con ambulancias y sus ubicaciones.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Path
from src.businessLayer.businessWorkflow.actualizarDisponibilidadAmbulancia import ActualizarDisponibilidadAmbulancia
from src.businessLayer.businessWorkflow.procesarUbicacionAmbulancia import ProcesarUbicacionAmbulancia
import json

websocket_ambulancias_router = APIRouter(
    prefix="/ws",
    tags=["websocket-ambulancias"]
)


@websocket_ambulancias_router.websocket("/ambulancias/{id_ambulancia}")
async def websocket_ambulancia(
    websocket: WebSocket,
    id_ambulancia: int = Path(..., gt=0, description="ID de la ambulancia")
):
    """
    Endpoint WebSocket específico para ambulancias.
    
    Permite comunicación en tiempo real relacionada con ambulancias.
    Las ambulancias se conectan aquí usando su ID para enviar continuamente
    su ubicación. Al conectar, la ambulancia se marca como disponible.
    Al desconectar, se marca como no disponible.
    
    Formato del mensaje esperado:
    {
        "ubicacion": {
            "latitud": 4.7110,
            "longitud": -74.0721
        }
    }
    
    Args:
        websocket: Conexión WebSocket.
        id_ambulancia: ID de la ambulancia que se conecta.
    """
    try:
        # Aceptar la conexión
        await websocket.accept()
        
        # Marcar la ambulancia como disponible al conectar
        try:
            ActualizarDisponibilidadAmbulancia.marcar_como_disponible(id_ambulancia)
        except ValueError as ve:
            await websocket.close(code=4004, reason=f"Error: {str(ve)}")
            return
        
        # Enviar mensaje de bienvenida
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": f"Conectado como ambulancia {id_ambulancia}! Listo para recibir ubicaciones",
            "id_ambulancia": id_ambulancia
        }))
        
        # Mantener la conexión activa escuchando mensajes de ubicación
        while True:
            try:
                # Recibir mensaje con la ubicación
                data = await websocket.receive_text()
                mensaje = json.loads(data)
                
                # Validar formato del mensaje
                if "ubicacion" not in mensaje:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Formato inválido. Se espera: {\"ubicacion\": {\"latitud\": X, \"longitud\": Y}}"
                    }))
                    continue
                
                ubicacion_data = mensaje["ubicacion"]
                if "latitud" not in ubicacion_data or "longitud" not in ubicacion_data:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Formato inválido. La ubicación debe contener 'latitud' y 'longitud'"
                    }))
                    continue
                
                # Procesar la ubicación
                try:
                    latitud = float(ubicacion_data["latitud"])
                    longitud = float(ubicacion_data["longitud"])
                    ProcesarUbicacionAmbulancia.procesar_ubicacion(id_ambulancia, latitud, longitud)
                    
                    # Confirmar recepción
                    await websocket.send_text(json.dumps({
                        "type": "ubicacion_recibida",
                        "message": "Ubicación actualizada correctamente"
                    }))
                except ValueError as ve:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(ve)
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Error al procesar ubicación: {str(e)}"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Formato JSON inválido"
                }))
            except Exception:
                break
                
    except WebSocketDisconnect:
        # Marcar la ambulancia como no disponible al desconectar
        try:
            ActualizarDisponibilidadAmbulancia.marcar_como_no_disponible(id_ambulancia)
        except:
            pass
    except Exception as e:
        # Log del error para debugging
        print(f"Error en websocket de ambulancia {id_ambulancia}: {e}")
        try:
            # Intentar marcar como no disponible en caso de error
            ActualizarDisponibilidadAmbulancia.marcar_como_no_disponible(id_ambulancia)
        except:
            pass

