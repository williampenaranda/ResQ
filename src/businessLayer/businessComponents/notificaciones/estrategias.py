"""
Estrategias concretas de notificación.
Implementaciones específicas para diferentes formas de enviar notificaciones.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, TYPE_CHECKING
from .estrategiaNotificacion import EstrategiaNotificacion

if TYPE_CHECKING:
    from .notificador import notificador

class EstrategiaBroadcast(EstrategiaNotificacion):
    """
    Estrategia para enviar notificaciones a todos los conectados (broadcast).
    Usada para operadores de emergencia que reciben todas las solicitudes.
    """
    
    async def enviar(self, notificador: 'notificador', tipo: str, datos: Dict[str, Any], **kwargs) -> None:
        message = json.dumps({
            "type": tipo,
            "data": datos,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await notificador.broadcast(message)


class EstrategiaPorID(EstrategiaNotificacion):
    """
    Estrategia para enviar notificaciones a un ID específico.
    Usada para solicitantes que reciben notificaciones personalizadas.
    """
    
    async def enviar(self, notificador: 'notificador', tipo: str, datos: Dict[str, Any], **kwargs) -> None:
        entity_id = kwargs.get('entity_id')
        if not entity_id:
            raise ValueError("EstrategiaPorID requiere 'entity_id' en kwargs")
        
        message = json.dumps({
            "type": tipo,
            "data": datos,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await notificador.send_to_id(message, entity_id)


class EstrategiaPorGrupo(EstrategiaNotificacion):
    """
    Estrategia para enviar notificaciones a múltiples IDs (grupo).
    Útil para notificar a varios operadores de ambulancia asignados a una emergencia.
    """
    
    async def enviar(self, notificador: 'notificador', tipo: str, datos: Dict[str, Any], **kwargs) -> None:
        entity_ids = kwargs.get('entity_ids', [])
        if not entity_ids:
            raise ValueError("EstrategiaPorGrupo requiere 'entity_ids' en kwargs")
        
        message = json.dumps({
            "type": tipo,
            "data": datos,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Enviar a cada ID del grupo
        for entity_id in entity_ids:
            await notificador.send_to_id(message, entity_id)

