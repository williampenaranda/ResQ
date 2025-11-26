"""
Gestor de tareas periódicas para enviar la ubicación en tiempo real de la ambulancia asignada
al websocket del solicitante.

Este módulo gestiona el envío periódico de la ubicación de la ambulancia que está atendiendo
una emergencia al solicitante que la reportó.
La ubicación se obtiene desde Redis donde se almacena en tiempo real.
"""

import asyncio
import json
from typing import Dict, Optional
from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import get_manager_solicitantes
from src.businessLayer.businessComponents.cache.configRedis import get_redis_client

# Diccionario para almacenar las tareas activas: {emergencia_id: task}
_tareas_activas: Dict[int, asyncio.Task] = {}

# Diccionario para mapear id_solicitante -> emergencia_id (para poder detener cuando se desconecta)
_solicitante_a_emergencia: Dict[int, int] = {}


async def _enviar_ubicacion_ambulancia_periodicamente(
    id_solicitante: int,
    emergencia_id: int,
    id_ambulancia: int
):
    """
    Tarea asíncrona que envía la ubicación de la ambulancia asignada cada segundo.
    Obtiene la ubicación desde Redis (donde se almacena en tiempo real).
    
    Args:
        id_solicitante: ID del solicitante que recibirá las actualizaciones
        emergencia_id: ID de la emergencia
        id_ambulancia: ID de la ambulancia asignada
    """
    manager = get_manager_solicitantes()
    client = get_redis_client()
    key_ubicacion = f"ambulancia:{id_ambulancia}:ubicacion"
    
    # Enviar la primera ubicación inmediatamente si está disponible
    try:
        valor_ubicacion_inicial = client.get(key_ubicacion)
        if valor_ubicacion_inicial:
            try:
                datos_ubicacion = json.loads(valor_ubicacion_inicial)
                latitud = datos_ubicacion.get('latitud')
                longitud = datos_ubicacion.get('longitud')
                
                if latitud is not None and longitud is not None:
                    mensaje = json.dumps({
                        "type": "ubicacion_ambulancia",
                        "latitud": latitud,
                        "longitud": longitud
                    })
                    await manager.send_to_id(mensaje, id_solicitante)
                    print(f"[DEBUG] Primera ubicación de ambulancia {id_ambulancia} enviada inmediatamente al solicitante {id_solicitante}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error al parsear ubicación inicial de ambulancia {id_ambulancia}: {e}")
    except Exception as e:
        print(f"Error al obtener ubicación inicial de ambulancia {id_ambulancia}: {e}")
    
    try:
        while True:
            try:
                # Verificar si hay conexiones activas para este solicitante
                if not manager.is_connected(id_solicitante):
                    # No hay conexiones activas, detener la tarea
                    print(f"No hay conexiones activas para solicitante {id_solicitante}, deteniendo envío de ubicación")
                    break
                
                # Obtener la ubicación de la ambulancia desde Redis
                valor_ubicacion = client.get(key_ubicacion)
                
                if valor_ubicacion:
                    try:
                        # Parsear JSON
                        datos_ubicacion = json.loads(valor_ubicacion)
                        
                        # Validar que tenga los campos necesarios
                        latitud = datos_ubicacion.get('latitud')
                        longitud = datos_ubicacion.get('longitud')
                        
                        if latitud is not None and longitud is not None:
                            # Preparar mensaje con type, latitud y longitud
                            mensaje = json.dumps({
                                "type": "ubicacion_ambulancia",
                                "latitud": latitud,
                                "longitud": longitud
                            })
                            
                            # Enviar al solicitante usando send_to_id
                            await manager.send_to_id(mensaje, id_solicitante)
                    
                    except (json.JSONDecodeError, KeyError) as e:
                        # Si hay error al parsear, continuar sin enviar esta vez
                        print(f"Error al parsear ubicación de ambulancia {id_ambulancia}: {e}")
                
                # Esperar 1 segundo antes de la siguiente iteración
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                # La tarea fue cancelada, salir del loop
                break
            except Exception as e:
                # Si hay un error, esperar un poco y continuar
                print(f"Error al enviar ubicación de ambulancia: {e}")
                await asyncio.sleep(1)
                
    except asyncio.CancelledError:
        # Tarea cancelada, limpiar
        if emergencia_id in _tareas_activas:
            del _tareas_activas[emergencia_id]
        # Limpiar el mapeo de solicitante a emergencia
        solicitantes_a_eliminar = [sid for sid, eid in _solicitante_a_emergencia.items() if eid == emergencia_id]
        for sid in solicitantes_a_eliminar:
            if sid in _solicitante_a_emergencia:
                del _solicitante_a_emergencia[sid]
    except Exception as e:
        print(f"Error en tarea periódica de ubicación de ambulancia para emergencia {emergencia_id}: {e}")
        if emergencia_id in _tareas_activas:
            del _tareas_activas[emergencia_id]
        # Limpiar el mapeo de solicitante a emergencia
        solicitantes_a_eliminar = [sid for sid, eid in _solicitante_a_emergencia.items() if eid == emergencia_id]
        for sid in solicitantes_a_eliminar:
            if sid in _solicitante_a_emergencia:
                del _solicitante_a_emergencia[sid]


def iniciar_envio_ubicacion_ambulancia(
    id_solicitante: int,
    emergencia_id: int,
    id_ambulancia: int
) -> bool:
    """
    Inicia el envío periódico de la ubicación de la ambulancia asignada al solicitante.
    
    Args:
        id_solicitante: ID del solicitante que recibirá las actualizaciones
        emergencia_id: ID de la emergencia
        id_ambulancia: ID de la ambulancia asignada
        
    Returns:
        True si se inició correctamente, False si ya existe una tarea para esta emergencia
    """
    # Si ya existe una tarea para esta emergencia, no crear otra
    if emergencia_id in _tareas_activas:
        return False
    
    # Crear la tarea asíncrona
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Si no hay loop corriendo, crear uno nuevo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    task = loop.create_task(
        _enviar_ubicacion_ambulancia_periodicamente(
            id_solicitante=id_solicitante,
            emergencia_id=emergencia_id,
            id_ambulancia=id_ambulancia
        )
    )
    
    _tareas_activas[emergencia_id] = task
    _solicitante_a_emergencia[id_solicitante] = emergencia_id
    return True


def detener_envio_ubicacion_ambulancia(emergencia_id: int) -> bool:
    """
    Detiene el envío periódico de la ubicación de la ambulancia para una emergencia.
    
    Args:
        emergencia_id: ID de la emergencia
        
    Returns:
        True si se detuvo correctamente, False si no había una tarea activa
    """
    if emergencia_id not in _tareas_activas:
        return False
    
    task = _tareas_activas[emergencia_id]
    
    # Cancelar la tarea
    if not task.done():
        task.cancel()
    
    # Remover de la lista de tareas activas
    del _tareas_activas[emergencia_id]
    
    # Limpiar el mapeo de solicitante a emergencia
    solicitantes_a_eliminar = [sid for sid, eid in _solicitante_a_emergencia.items() if eid == emergencia_id]
    for sid in solicitantes_a_eliminar:
        del _solicitante_a_emergencia[sid]
    
    return True


def detener_envio_por_solicitante(id_solicitante: int) -> bool:
    """
    Detiene el envío periódico de la ubicación de la ambulancia para un solicitante específico.
    Se usa cuando el websocket del solicitante se desconecta.
    
    Args:
        id_solicitante: ID del solicitante
        
    Returns:
        True si se detuvo correctamente, False si no había una tarea activa para ese solicitante
    """
    if id_solicitante not in _solicitante_a_emergencia:
        return False
    
    emergencia_id = _solicitante_a_emergencia[id_solicitante]
    return detener_envio_ubicacion_ambulancia(emergencia_id)


def hay_tarea_activa(emergencia_id: int) -> bool:
    """
    Verifica si hay una tarea activa para una emergencia.
    
    Args:
        emergencia_id: ID de la emergencia
        
    Returns:
        True si hay una tarea activa, False en caso contrario
    """
    return emergencia_id in _tareas_activas

