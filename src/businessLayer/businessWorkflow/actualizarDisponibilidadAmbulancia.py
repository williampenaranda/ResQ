"""
Workflow para actualizar la disponibilidad de una ambulancia.
"""

from src.businessLayer.businessComponents.entidades.servicioAmbulancia import ServicioAmbulancia


class ActualizarDisponibilidadAmbulancia:
    """
    Workflow para actualizar la disponibilidad de una ambulancia.
    """

    @staticmethod
    def marcar_como_disponible(id_ambulancia: int) -> None:
        """
        Marca una ambulancia como disponible.

        Args:
            id_ambulancia: ID de la ambulancia a marcar como disponible

        Raises:
            ValueError: Si la ambulancia no existe o el ID es inválido
        """
        ambulancia = ServicioAmbulancia.obtener_por_id(id_ambulancia)
        if not ambulancia:
            raise ValueError(f"Ambulancia con id {id_ambulancia} no encontrada")

        ambulancia.set_disponibilidad(True)
        actualizada = ServicioAmbulancia.actualizar(id_ambulancia, {"disponibilidad": True})
        if not actualizada:
            raise ValueError(f"Error al actualizar la disponibilidad de la ambulancia {id_ambulancia}")

    @staticmethod
    def marcar_como_no_disponible(id_ambulancia: int) -> None:
        """
        Marca una ambulancia como no disponible.

        Args:
            id_ambulancia: ID de la ambulancia a marcar como no disponible

        Raises:
            ValueError: Si la ambulancia no existe o el ID es inválido
        """
        ambulancia = ServicioAmbulancia.obtener_por_id(id_ambulancia)
        if not ambulancia:
            raise ValueError(f"Ambulancia con id {id_ambulancia} no encontrada")

        ambulancia.set_disponibilidad(False)
        actualizada = ServicioAmbulancia.actualizar(id_ambulancia, {"disponibilidad": False})
        if not actualizada:
            raise ValueError(f"Error al actualizar la disponibilidad de la ambulancia {id_ambulancia}")

