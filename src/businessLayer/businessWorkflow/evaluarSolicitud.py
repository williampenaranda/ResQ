"""
Workflow para evaluar una solicitud y crear una emergencia.
Este workflow orquesta la creación de emergencias y las notificaciones correspondientes.
"""

from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessComponents.entidades.servicioEmergencia import ServicioEmergencia
from src.dataLayer.dataAccesComponets.repositorioSolicitudes import obtener_solicitud_por_id
from src.dataLayer.dataAccesComponets.repositorioSolicitantes import obtener_solicitante_por_id
from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import notificar_emergencia_evaluada


class EvaluarSolicitud:
    """
    Workflow para evaluar una solicitud y crear una emergencia.
    """

    @staticmethod
    async def evaluar_solicitud(
        solicitud_id: int,
        estado,
        tipo_ambulancia,
        nivel_prioridad,
        descripcion: str,
        id_operador: int,
        solicitante_id: int
    ) -> Emergencia:
        """
        Evalúa una solicitud y crea una emergencia, luego notifica al solicitante.

        Args:
            solicitud_id: ID de la solicitud a evaluar
            estado: Estado de la emergencia (EstadoEmergencia)
            tipo_ambulancia: Tipo de ambulancia requerida (TipoAmbulancia)
            nivel_prioridad: Nivel de prioridad (NivelPrioridad)
            descripcion: Descripción de la emergencia
            id_operador: ID del operador asignado
            solicitante_id: ID del solicitante

        Returns:
            Emergencia: La emergencia creada

        Raises:
            ValueError: Si algún parámetro es inválido
            RuntimeError: Si no se encuentra la solicitud o el solicitante
        """
        from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
        from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
        from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad

        # Validar que los enums sean del tipo correcto
        if not isinstance(estado, EstadoEmergencia):
            raise ValueError(f"El estado debe ser una instancia de EstadoEmergencia, recibido: {type(estado)}")
        if not isinstance(tipo_ambulancia, TipoAmbulancia):
            raise ValueError(f"El tipo de ambulancia debe ser una instancia de TipoAmbulancia, recibido: {type(tipo_ambulancia)}")
        if not isinstance(nivel_prioridad, NivelPrioridad):
            raise ValueError(f"El nivel de prioridad debe ser una instancia de NivelPrioridad, recibido: {type(nivel_prioridad)}")

        # Obtener la solicitud
        solicitud = obtener_solicitud_por_id(solicitud_id)
        if not solicitud:
            raise ValueError(f"Solicitud con id {solicitud_id} no encontrada")

        # Obtener el solicitante
        solicitante = obtener_solicitante_por_id(solicitante_id)
        if not solicitante:
            raise ValueError(f"Solicitante con id {solicitante_id} no encontrado")

        # Crear la entidad Emergencia
        emergencia = Emergencia(
            id=None,
            solicitud=solicitud,
            estado=estado,
            tipoAmbulancia=tipo_ambulancia,
            nivelPrioridad=nivel_prioridad,
            descripcion=descripcion,
            id_operador=id_operador,
            solicitante=solicitante
        )

        # Crear la emergencia usando el servicio
        creada = ServicioEmergencia.crear(emergencia)
        if creada is None:
            raise RuntimeError("Error al crear la emergencia. Verifique que todos los IDs sean válidos.")

        # Notificar a los solicitantes sobre la nueva emergencia
        # Usar mode='json' para convertir date/datetime a strings serializables
        await notificar_emergencia_evaluada(
            creada.solicitante.id,
            creada.model_dump(mode='json')
        )

        return creada

