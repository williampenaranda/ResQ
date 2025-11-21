"""
Interfaz abstracta para estrategias de notificación.
Define cómo se envía una notificación según el tipo de entidad.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .notificador import notificador

class EstrategiaNotificacion(ABC):
    """
    Interfaz para estrategias de notificación.
    Define cómo se envía una notificación según el tipo de entidad.
    """
    
    @abstractmethod
    async def enviar(self, notificador: 'notificador', tipo: str, datos: Dict[str, Any], **kwargs) -> None:
        """
        Envía una notificación usando la estrategia específica.
        
        Args:
            notificador: Instancia del notificador con las conexiones (objeto de tipo notificador, no string)
            tipo: Tipo de notificación
            datos: Datos de la notificación
            **kwargs: Parámetros adicionales específicos de la estrategia
        """
        pass

