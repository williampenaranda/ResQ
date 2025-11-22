"""
Workflow para emitir una orden de despacho.
Este workflow orquesta la creación de órdenes de despacho y las notificaciones correspondientes.
"""

from datetime import datetime
from src.businessLayer.businessEntities.ordenDespacho import OrdenDespacho
from src.businessLayer.businessComponents.entidades.servicioOrdenDespacho import ServicioOrdenDespacho
from src.dataLayer.dataAccesComponets.repositorioEmergencias import obtener_emergencia_por_id
from src.dataLayer.dataAccesComponets.repositorioAmbulancia import obtener_ambulancia_por_id
from src.dataLayer.dataAccesComponets.repositorioOperadorAmbulancia import obtener_operador_por_id as obtener_operador_ambulancia_por_id
from src.dataLayer.dataAccesComponets.repositorioOperadorEmergencia import obtener_operador_por_id as obtener_operador_emergencia_por_id
from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import notificar_emergencia_despachada


class EmitirOrdenDespacho:
    """
    Workflow para emitir una orden de despacho.
    """

    @staticmethod
    async def emitir_orden_despacho(
        emergencia_id: int,
        ambulancia_id: int,
        operador_ambulancia_id: int,
        operador_emergencia_id: int,
        fecha_hora: datetime = None
    ) -> OrdenDespacho:
        """
        Emite una orden de despacho, asignando una ambulancia y operadores a una emergencia.

        Args:
            emergencia_id: ID de la emergencia a atender
            ambulancia_id: ID de la ambulancia asignada
            operador_ambulancia_id: ID del operador de ambulancia asignado
            operador_emergencia_id: ID del operador de emergencia que emite la orden
            fecha_hora: Fecha y hora de la orden (opcional, por defecto usa la hora actual)

        Returns:
            OrdenDespacho: La orden de despacho creada

        Raises:
            ValueError: Si algún parámetro es inválido
            RuntimeError: Si no se encuentra alguna de las entidades relacionadas
        """
        # Si no se proporciona fecha_hora, usar la hora actual
        if fecha_hora is None:
            fecha_hora = datetime.now()

        # Validar que fecha_hora sea del tipo correcto
        if not isinstance(fecha_hora, datetime):
            raise ValueError(f"La fecha y hora debe ser una instancia de datetime, recibido: {type(fecha_hora)}")

        # Obtener la emergencia
        emergencia = obtener_emergencia_por_id(emergencia_id)
        if not emergencia:
            raise ValueError(f"Emergencia con id {emergencia_id} no encontrada")

        # Obtener la ambulancia
        ambulancia = obtener_ambulancia_por_id(ambulancia_id)
        if not ambulancia:
            raise ValueError(f"Ambulancia con id {ambulancia_id} no encontrada")

        # Validar que la ambulancia esté disponible
        if not ambulancia.get_disponibilidad():
            raise ValueError(f"La ambulancia con id {ambulancia_id} no está disponible")

        # Obtener el operador de ambulancia
        operador_ambulancia = obtener_operador_ambulancia_por_id(operador_ambulancia_id)
        if not operador_ambulancia:
            raise ValueError(f"Operador de ambulancia con id {operador_ambulancia_id} no encontrado")

        # Obtener el operador de emergencia
        operador_emergencia = obtener_operador_emergencia_por_id(operador_emergencia_id)
        if not operador_emergencia:
            raise ValueError(f"Operador de emergencia con id {operador_emergencia_id} no encontrado")

        # Crear la entidad OrdenDespacho
        orden_despacho = OrdenDespacho(
            id=None,
            fechaHora=fecha_hora,
            emergencia=emergencia,
            ambulancia=ambulancia,
            operadorAmbulancia=operador_ambulancia,
            operadorEmergencia=operador_emergencia
        )

        # Crear la orden de despacho usando el servicio
        creada = ServicioOrdenDespacho.crear(orden_despacho)
        if creada is None:
            raise RuntimeError("Error al crear la orden de despacho. Verifique que todos los IDs sean válidos.")

        # Notificar a los operadores de emergencia sobre la nueva orden de despacho
        # Usar mode='json' para convertir date/datetime a strings serializables
        
        await notificar_emergencia_despachada(
            creada.solicitante.id,
            creada.model_dump(mode='json')
        )

        return creada
