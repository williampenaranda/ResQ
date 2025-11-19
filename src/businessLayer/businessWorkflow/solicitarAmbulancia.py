from datetime import datetime
from src.dataLayer.dataAccesComponets.repositorioSolicitudes import crear_solicitud as repo_crear_solicitud
from src.dataLayer.dataAccesComponets.repositorioUbicacion import crear_ubicacion as repo_crear_ubicacion
from src.businessLayer.businessEntities.solicitud import Solicitud
from src.businessLayer.businessComponents.llamadas.crearSala import crearSala
from src.businessLayer.businessComponents.llamadas.tokenLlamadas import generar_token_participante
from src.businessLayer.businessComponents.llamadas.configLiveKit import (
    LIVEKIT_URL,
    validate_livekit_config,
)
from src.comunication.notificadorEmergencias import notificar_nueva_solicitud
import uuid

class SolicitarAmbulancia:

    @staticmethod
    async def registrarSolicitud(solicitud: Solicitud | dict) -> dict:
        if isinstance(solicitud, dict):
            solicitud_obj = Solicitud.model_validate(solicitud)
            solicitud_dict = solicitud
        else:
            solicitud_obj = solicitud
            solicitud_dict = solicitud.model_dump(mode="json")
        # Validaciones básicas
        if solicitud_obj is None:
            raise ValueError("La solicitud no puede ser None")
        if not solicitud_obj.solicitante or not solicitud_obj.solicitante.nombre:
            raise ValueError("La solicitud debe incluir un solicitante con nombre")

        # Si la ubicación no tiene ID, crearla primero en la base de datos
        if not solicitud_obj.ubicacion.id:
            ubicacion_creada = repo_crear_ubicacion(solicitud_obj.ubicacion)
            if ubicacion_creada is None:
                raise ValueError("Error al crear la ubicación")
            # Actualizar la solicitud con la ubicación que tiene ID
            solicitud_obj.ubicacion = ubicacion_creada

        solicitud_creada = repo_crear_solicitud(solicitud_obj)
        if solicitud_creada is None:
            raise ValueError("Error al crear la solicitud")

        # Validar configuración de LiveKit antes de operar
        validate_livekit_config()

        # Generar nombre de sala único
        nombreSala = f"emergencia-{uuid.uuid4()}"

        # Crear sala (máximo 2 participantes: solicitante y operador/médico)
        await crearSala(nombreSala, max_participants=2)

        # Generar identidad y token con permisos de unirse y audio
        identidad, token = generar_token_participante(
            nombre=solicitud_obj.solicitante.nombre,
            nombre_sala=nombreSala
        )

        # Preparar datos de la solicitud para notificar
        datos_solicitud = solicitud_creada.model_dump(mode="json")
        
        # Notificar nueva solicitud con el nombre de la sala
        await notificar_nueva_solicitud(
            nombre_sala=nombreSala,
            datos_solicitud=datos_solicitud
        )

        return {
            "room": nombreSala,
            "token": token,
            "identity": identidad,
            "server_url": LIVEKIT_URL,
            "solicitud": datos_solicitud,
        }