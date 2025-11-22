"""
Componente de comunicación para notificar eventos relacionados con ambulancias
a través del WebSocket de ambulancias.
"""

from typing import Dict, Any
from src.businessLayer.businessComponents.notificaciones.notificador import notificador
from src.businessLayer.businessComponents.notificaciones.estrategias import EstrategiaPorID

# Manager específico para ambulancias con estrategia por ID
manager_ambulancias = notificador(estrategia=EstrategiaPorID())


async def notificar_orden_despacho(id_ambulancia: int, datos_orden: Dict[str, Any]):
    """
    Notifica a una ambulancia específica que se le ha asignado una orden de despacho.

    Args:
        id_ambulancia: ID de la ambulancia.
        datos_orden: Diccionario con la información de la orden de despacho.
    """
    await manager_ambulancias.notificar(
        tipo="orden_despacho",
        datos=datos_orden,
        entity_id=id_ambulancia
    )


def get_manager_ambulancias() -> notificador:
    """
    Obtiene el manager de conexiones de ambulancias.
    
    Returns:
        notificador: Instancia del manager de conexiones de ambulancias.
    """
    return manager_ambulancias
