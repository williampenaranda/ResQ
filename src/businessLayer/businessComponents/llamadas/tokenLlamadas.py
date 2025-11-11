from typing import Tuple
import uuid
from livekit import api
from src.businessLayer.businessComponents.llamadas.configLiveKit import (
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    validate_livekit_config,
)

def generar_token_participante(nombre: str, nombre_sala: str) -> Tuple[str, str]:
    """
    Genera un token JWT para un participante con permisos de unirse,
    enviar audio y recibir audio en una sala especificada de LiveKit.

    Args:
        nombre: Nombre a mostrar para el participante.
        nombre_sala: Nombre de la sala de LiveKit a la que se unirá.

    Returns:
        Una tupla con (identidad_generada, token_jwt).

    Raises:
        ValueError: Si los parámetros son inválidos o falta configuración.
    """
    if not nombre or not isinstance(nombre, str):
        raise ValueError("El nombre del participante debe ser una cadena no vacía")

    if not nombre_sala or not isinstance(nombre_sala, str):
        raise ValueError("El nombre de la sala debe ser una cadena no vacía")

    # Limpieza básica
    nombre = nombre.strip()
    nombre_sala = nombre_sala.strip()

    if not nombre or not nombre_sala:
        raise ValueError("Nombre y sala no pueden estar vacíos")

    # Verificar que las variables de entorno necesarias estén configuradas
    validate_livekit_config()

    # Generar una identidad única (p. ej., combinación de nombre con un UUID corto)


    # Crear el token con permisos solo de unión y audio (hablar/escuchar)
    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(nombre)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=nombre_sala,
                can_publish=True,          # Permitir compartir audio
                can_subscribe=True,        # Permitir escuchar
                can_publish_data=False,    # Opcional: deshabilitar data channels si no se necesitan
                can_publish_sources=("microphone",),  # Limitar a audio
                can_subscribe_sources=("microphone",),# Recibir solo audio
            )
        )
        .to_jwt()
    )

    return token