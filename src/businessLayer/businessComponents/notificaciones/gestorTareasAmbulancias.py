"""
Gestor de tareas periódicas para enviar información de ambulancias a operadores de emergencia.

Este módulo gestiona el envío periódico de información de ambulancias disponibles
a los operadores de emergencia que están evaluando una emergencia.
Las ambulancias se obtienen desde Redis donde se almacenan sus ubicaciones en tiempo real.
"""

import asyncio
import json
from typing import Dict, Optional
from src.businessLayer.businessComponents.notificaciones.notificadorOperadorEmergencias import get_manager_operadores_emergencia
from src.businessLayer.businessComponents.entidades.buscarAmbulanciaCercana import BuscarAmbulanciaCercana
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia

# Diccionario para almacenar las tareas activas: {emergencia_id: task}
_tareas_activas: Dict[int, asyncio.Task] = {}


async def _enviar_info_ambulancias_periodicamente(
    id_operador: int,
    emergencia_id: int,
    tipo_ambulancia: TipoAmbulancia
):
    """
    Tarea asíncrona que envía información de ambulancias cada segundo.
    Obtiene las ambulancias desde Redis (las que están conectadas y enviando ubicaciones).
    
    Args:
        id_operador: ID del operador de emergencia que está evaluando
        emergencia_id: ID de la emergencia que se está evaluando
        tipo_ambulancia: Tipo de ambulancia requerida para filtrar
    """
    manager = get_manager_operadores_emergencia()
    
    try:
        while True:
            try:
                # Obtener todas las ambulancias conectadas desde Redis
                ambulancias_conectadas = BuscarAmbulanciaCercana._obtener_todas_las_ambulancias_conectadas()
                
                # Filtrar por tipo de ambulancia requerido
                tipo_requerido = tipo_ambulancia.value
                ambulancias_filtradas = [
                    (id_amb, datos) for id_amb, datos in ambulancias_conectadas
                    if datos.get('tipoAmbulancia') == tipo_requerido
                ]
                
                # Preparar datos para enviar (solo id, latitud, longitud)
                datos_ambulancias = []
                for id_ambulancia, datos_ubicacion in ambulancias_filtradas:
                    datos_ambulancia = {
                        "id": id_ambulancia,
                        "latitud": datos_ubicacion.get('latitud'),
                        "longitud": datos_ubicacion.get('longitud')
                    }
                    
                    datos_ambulancias.append(datos_ambulancia)
                
                # Enviar información al operador
                mensaje = json.dumps({
                    "type": "info_ambulancias",
                    "emergencia_id": emergencia_id,
                    "ambulancias": datos_ambulancias,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # Enviar a todas las conexiones del operador usando send_to_id
                await manager.send_to_id(mensaje, id_operador)
                
                # Esperar 1 segundo antes de la siguiente iteración
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                # La tarea fue cancelada, salir del loop
                break
            except Exception as e:
                # Si hay un error, esperar un poco y continuar
                print(f"Error al enviar información de ambulancias: {e}")
                await asyncio.sleep(1)
                
    except asyncio.CancelledError:
        # Tarea cancelada, limpiar
        if emergencia_id in _tareas_activas:
            del _tareas_activas[emergencia_id]
    except Exception as e:
        print(f"Error en tarea periódica de ambulancias para emergencia {emergencia_id}: {e}")
        if emergencia_id in _tareas_activas:
            del _tareas_activas[emergencia_id]


def iniciar_envio_ambulancias(
    id_operador: int,
    emergencia_id: int,
    tipo_ambulancia: TipoAmbulancia
) -> bool:
    """
    Inicia el envío periódico de información de ambulancias a un operador de emergencia.
    
    Args:
        id_operador: ID del operador de emergencia
        emergencia_id: ID de la emergencia que se está evaluando
        tipo_ambulancia: Tipo de ambulancia requerida
        
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
        _enviar_info_ambulancias_periodicamente(
            id_operador=id_operador,
            emergencia_id=emergencia_id,
            tipo_ambulancia=tipo_ambulancia
        )
    )
    
    _tareas_activas[emergencia_id] = task
    return True


def detener_envio_ambulancias(emergencia_id: int) -> bool:
    """
    Detiene el envío periódico de información de ambulancias para una emergencia.
    
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
    
    return True


def hay_tarea_activa(emergencia_id: int) -> bool:
    """
    Verifica si hay una tarea activa para una emergencia.
    
    Args:
        emergencia_id: ID de la emergencia
        
    Returns:
        True si hay una tarea activa, False en caso contrario
    """
    return emergencia_id in _tareas_activas

