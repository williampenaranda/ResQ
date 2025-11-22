"""
Componente de comunicación para notificar eventos relacionados con solicitudes
a través del WebSocket de solicitantes.
"""

from typing import Dict, Any
from src.businessLayer.businessComponents.notificaciones.notificador import notificador
from src.businessLayer.businessComponents.notificaciones.estrategias import EstrategiaPorID

# Manager específico para solicitantes con estrategia por ID
manager_solicitantes = notificador(estrategia=EstrategiaPorID())


async def notificar_estado_Emergencia(id_solicitante: int, tipo: str, datos: Dict[str, Any]):
    """
    Notifica a un solicitante específico sobre cambios en el estado de su solicitud.

    Args:
        id_solicitante: ID del solicitante destinatario.
        tipo: Tipo de notificación (ej: "evaluada", "asignada ", "resuelta").
        datos: Diccionario con la información de la notificación.
    """
    await manager_solicitantes.notificar(
        tipo=tipo,
        datos=datos,
        entity_id=id_solicitante
    )


async def notificar_emergencia_evaluada(id_solicitante: int, datos_emergencia: Dict[str, Any]):
    """
    Notifica a un solicitante que su emergencia ha sido evaluada.

    Args:
        id_solicitante: ID del solicitante.
        datos_emergencia: Diccionario con la información de la emergencia evaluada.
    """
    await notificar_estado_Emergencia(
        id_solicitante=id_solicitante,
        tipo="EstadoEmergencia.EVALUADA",
        datos=datos_emergencia
    )


async def notificar_emergencia_despachada(id_solicitante: int, datos_orden: Dict[str, Any]):
    """
    Notifica a un solicitante que se ha despachado una ambulancia para su emergencia.

    Args:
        id_solicitante: ID del solicitante.
        datos_orden: Diccionario con la información de la orden de despacho.
    """
    await notificar_estado_Emergencia(
        id_solicitante=id_solicitante,
        tipo="EstadoEmergencia.DESPACHADA",
        datos=datos_orden
    )


def get_manager_solicitantes() -> notificador:
    """
    Obtiene el manager de conexiones de solicitantes.
    
    Returns:
        notificador: Instancia del manager de conexiones de solicitantes.
    """
    return manager_solicitantes

