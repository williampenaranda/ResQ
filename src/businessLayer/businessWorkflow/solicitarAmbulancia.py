from src.businessLayer.businessEntities.solicitud import Solicitud
from src.businessLayer.businessComponents.llamadas.crearSala import crearSala
from src.businessLayer.businessComponents.llamadas.tokenLlamadas import generar_token_participante
from src.businessLayer.businessComponents.llamadas.configLiveKit import (
    LIVEKIT_URL,
    validate_livekit_config,
)
import uuid

class SolicitarAmbulancia:

    @staticmethod
    async def registrarSolicitud(solicitud: Solicitud) -> dict:
        # Validaciones básicas
        if solicitud is None:
            raise ValueError("La solicitud no puede ser None")
        if not solicitud.solicitante or not solicitud.solicitante.nombre:
            raise ValueError("La solicitud debe incluir un solicitante con nombre")

        # Validar configuración de LiveKit antes de operar
        validate_livekit_config()

        # Generar nombre de sala único
        nombreSala = f"emergencia-{uuid.uuid4()}"

        # Crear sala (máximo 2 participantes: solicitante y operador/médico)
        await crearSala(nombreSala, max_participants=2)

        # Generar identidad y token con permisos de unirse y audio
        identidad, token = generar_token_participante(
            nombre=solicitud.solicitante.nombre,
            nombre_sala=nombreSala
        )

        return {
            "room": nombreSala,
            "token": token,
            "identity": identidad,
            "server_url": LIVEKIT_URL,
        }