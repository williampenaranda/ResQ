"""
Componente de comunicación para notificar eventos relacionados con emergencias
a través del WebSocket de operadores de emergencia.
"""

from typing import Dict, Any
from src.businessLayer.businessComponents.notificaciones.notificador import notificador
from src.businessLayer.businessComponents.notificaciones.estrategias import EstrategiaBroadcast

# Manager específico para operadores de emergencia con estrategia de broadcast
manager_operadores_emergencia = notificador(estrategia=EstrategiaBroadcast())


async def notificar_nueva_solicitud(nombre_sala: str, datos_solicitud: Dict[str, Any]):
    """
    Notifica a todos los clientes conectados al WebSocket de emergencias
    sobre una nueva solicitud recibida, incluyendo el nombre de la sala.

    Args:
        nombre_sala: Nombre de la sala creada para la emergencia.
        datos_solicitud: Diccionario con la información de la solicitud.
    """
    await manager_operadores_emergencia.notificar(
        tipo="nueva_solicitud",
        datos={
            **datos_solicitud,
            "room": nombre_sala
        }
    )


async def notificar_sala_atendida(nombre_sala: str):
    """
    Notifica a todos los clientes conectados al WebSocket de emergencias
    que una sala ha sido atendida (está llena con 2 participantes).

    Args:
        nombre_sala: Nombre de la sala que ha sido atendida.
    """
    await manager_operadores_emergencia.notificar(
        tipo="sala_atendida",
        datos={
            "room": nombre_sala,
            "estado": "atendida"
        }
    )


def get_manager_operadores_emergencia() -> notificador:
    """
    Obtiene el manager de conexiones de operadores de emergencia.
    
    Returns:
        notificador: Instancia del manager de conexiones de operadores de emergencia.
    """
    return manager_operadores_emergencia

