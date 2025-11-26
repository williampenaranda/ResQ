"""
Gestor de tareas periódicas para enviar información de ambulancias a operadores de emergencia.

Este módulo gestiona el envío periódico de la ubicación de la ambulancia más cercana (óptima)
a los operadores de emergencia que están evaluando una emergencia.
La ubicación se obtiene desde Redis donde se almacena en tiempo real.
"""

import asyncio
import json
from typing import Dict, Optional
from src.businessLayer.businessComponents.notificaciones.notificadorOperadorEmergencias import get_manager_operadores_emergencia
from src.businessLayer.businessComponents.entidades.buscarAmbulanciaCercana import BuscarAmbulanciaCercana
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.businessLayer.businessComponents.cache.configRedis import get_redis_client

# Diccionario para almacenar las tareas activas: {emergencia_id: task}
_tareas_activas: Dict[int, asyncio.Task] = {}


async def _enviar_info_ambulancias_periodicamente(
    id_operador: int,
    emergencia_id: int,
    tipo_ambulancia: TipoAmbulancia,
    ubicacion_emergencia: Ubicacion,
    nivel_prioridad: NivelPrioridad
):
    """
    Tarea asíncrona que envía la ubicación de la ambulancia más cercana cada segundo.
    Obtiene la ubicación desde Redis (donde se almacena en tiempo real).
    
    Args:
        id_operador: ID del operador de emergencia que está evaluando
        emergencia_id: ID de la emergencia que se está evaluando
        tipo_ambulancia: Tipo de ambulancia requerida para filtrar
        ubicacion_emergencia: Ubicación de la emergencia para calcular la ambulancia más cercana
        nivel_prioridad: Nivel de prioridad de la emergencia
    """
    manager = get_manager_operadores_emergencia()
    client = get_redis_client()
    
    try:
        while True:
            try:
                # Verificar si hay conexiones activas para este operador
                if not manager.is_connected(id_operador):
                    # No hay conexiones activas, detener la tarea
                    print(f"No hay conexiones activas para operador {id_operador}, deteniendo envío de ubicación")
                    break
                
                # Encontrar la ambulancia más cercana
                id_ambulancia_cercana = BuscarAmbulanciaCercana.encontrar_mas_cercana(
                    ubicacion_emergencia=ubicacion_emergencia,
                    tipo_ambulancia=tipo_ambulancia,
                    nivel_prioridad=nivel_prioridad
                )
                
                if id_ambulancia_cercana is not None:
                    # Obtener la ubicación de la ambulancia desde Redis
                    key_ubicacion = f"ambulancia:{id_ambulancia_cercana}:ubicacion"
                    valor_ubicacion = client.get(key_ubicacion)
                    
                    if valor_ubicacion:
                        try:
                            # Parsear JSON
                            datos_ubicacion = json.loads(valor_ubicacion)
                            
                            # Validar que tenga los campos necesarios
                            latitud = datos_ubicacion.get('latitud')
                            longitud = datos_ubicacion.get('longitud')
                            
                            if latitud is not None and longitud is not None:
                                # Preparar mensaje con tipo, latitud y longitud (mismo formato que para solicitantes)
                                mensaje = json.dumps({
                                    "tipo": "ubicacion_ambulancia",
                                    "latitud": latitud,
                                    "longitud": longitud
                                })
                                
                                # Enviar al operador usando send_to_id
                                await manager.send_to_id(mensaje, id_operador)
                        
                        except (json.JSONDecodeError, KeyError) as e:
                            # Si hay error al parsear, continuar sin enviar esta vez
                            print(f"Error al parsear ubicación de ambulancia {id_ambulancia_cercana}: {e}")
                
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
    except Exception as e:
        print(f"Error en tarea periódica de ambulancias para emergencia {emergencia_id}: {e}")
        if emergencia_id in _tareas_activas:
            del _tareas_activas[emergencia_id]


def iniciar_envio_ambulancias(
    id_operador: int,
    emergencia_id: int,
    tipo_ambulancia: TipoAmbulancia,
    ubicacion_emergencia: Ubicacion,
    nivel_prioridad: NivelPrioridad
) -> bool:
    """
    Inicia el envío periódico de la ubicación de la ambulancia más cercana a un operador de emergencia.
    
    Args:
        id_operador: ID del operador de emergencia
        emergencia_id: ID de la emergencia que se está evaluando
        tipo_ambulancia: Tipo de ambulancia requerida
        ubicacion_emergencia: Ubicación de la emergencia para calcular la ambulancia más cercana
        nivel_prioridad: Nivel de prioridad de la emergencia
        
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
            tipo_ambulancia=tipo_ambulancia,
            ubicacion_emergencia=ubicacion_emergencia,
            nivel_prioridad=nivel_prioridad
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

