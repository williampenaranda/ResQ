from src.businessLayer.businessComponents.actores.servicioOperadorEmergencia import ServicioOperadorEmergencia
from src.businessLayer.businessComponents.llamadas.unirseSala import generar_token_unirse_sala
from src.businessLayer.businessComponents.llamadas.obtenerParticipantesSala import (
    obtener_numero_participantes,
    obtener_max_participantes
)
from src.businessLayer.businessComponents.llamadas.configLiveKit import (
    LIVEKIT_URL,
    validate_livekit_config,
)
from src.comunication.notificadorEmergencias import notificar_sala_atendida


class UnirseSalaEmergencia:
    """
    Workflow para que un operador de emergencia se una a una sala existente.
    Obtiene los datos del operador, valida la configuración y genera las credenciales de acceso.
    """

    @staticmethod
    async def unirse_a_sala(id_operador: int, nombre_sala: str) -> dict:
        """
        Procesa la solicitud de un operador para unirse a una sala de emergencia existente.

        Args:
            id_operador: ID del operador de emergencia que se unirá a la sala.
            nombre_sala: Nombre de la sala de LiveKit a la que se unirá.

        Returns:
            Diccionario con:
            - room: Nombre de la sala
            - token: Token JWT para acceder a la sala
            - identity: Identidad generada para el participante
            - server_url: URL del servidor de LiveKit

        Raises:
            ValueError: Si los parámetros son inválidos o el operador no existe.
        """
        # Validaciones básicas
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("El ID del operador debe ser un entero positivo")

        if not nombre_sala or not isinstance(nombre_sala, str):
            raise ValueError("El nombre de la sala debe ser una cadena no vacía")

        nombre_sala = nombre_sala.strip()
        if not nombre_sala:
            raise ValueError("El nombre de la sala no puede estar vacío")

        # Obtener el operador de emergencia
        operador = ServicioOperadorEmergencia.obtener_por_id(id_operador)
        if not operador:
            raise ValueError(f"Operador de emergencia con ID {id_operador} no encontrado")

        # Validar configuración de LiveKit antes de operar
        validate_livekit_config()

        # Construir nombre completo del operador para la identidad
        nombre_completo = operador.nombre
        if operador.nombre2:
            nombre_completo += f" {operador.nombre2}"
        nombre_completo += f" {operador.apellido}"
        if operador.apellido2:
            nombre_completo += f" {operador.apellido2}"

        # Generar identidad y token con permisos de unirse y audio
        identidad, token = generar_token_unirse_sala(
            nombre=nombre_completo,
            nombre_sala=nombre_sala
        )

        # Verificar si la sala quedará llena después de que el operador se una
        # Las salas de emergencia tienen máximo 2 participantes (solicitante + operador)
        # Si actualmente hay 1 participante (el solicitante), al unirse el operador la sala quedará llena
        num_participantes_actuales = await obtener_numero_participantes(nombre_sala)
        max_participantes = await obtener_max_participantes(nombre_sala)
        
        # Si al unirse el operador la sala quedará llena (participantes actuales + 1 >= max)
        if num_participantes_actuales + 1 >= max_participantes:
            await notificar_sala_atendida(nombre_sala)

        return {
            "room": nombre_sala,
            "token": token,
            "identity": identidad,
            "server_url": LIVEKIT_URL,
        }

