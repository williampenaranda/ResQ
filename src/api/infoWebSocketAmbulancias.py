"""
Router para endpoints de información sobre WebSocket de ambulancias.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

class WebSocketInfoAmbulanciaResponse(BaseModel):
    websocket_url: str = Field(..., description="URL del endpoint WebSocket para conectarse (requiere {id_ambulancia})")
    conexiones_activas: int = Field(..., description="Número de ambulancias conectadas actualmente")
    descripcion: str = Field(..., description="Descripción del endpoint WebSocket")
    formato_mensaje: dict = Field(..., description="Ejemplo del formato JSON esperado para enviar ubicaciones")


info_websocket_ambulancias_router = APIRouter(
    prefix="/info-websocket-ambulancias",
    tags=["info-websocket-ambulancias"]
)


@info_websocket_ambulancias_router.get(
    "/websocket-info",
    response_model=WebSocketInfoAmbulanciaResponse,
    summary="Información sobre el WebSocket de ambulancias",
    description=(
        "Proporciona información sobre cómo conectarse al WebSocket para enviar ubicaciones "
        "en tiempo real. Las ambulancias deben conectarse a este endpoint usando su ID para "
        "enviar continuamente su ubicación. Al conectar, la ambulancia se marca automáticamente "
        "como disponible. Al desconectar, se marca como no disponible."
    ),
)
async def obtener_info_websocket_ambulancia(request: Request) -> WebSocketInfoAmbulanciaResponse:
    """
    Retorna información sobre cómo conectarse al WebSocket de ambulancias.
    
    Este endpoint proporciona:
    - La URL del WebSocket (requiere el ID de la ambulancia como parámetro)
    - El número de conexiones activas (si está disponible)
    - Ejemplos del formato de mensajes esperados
    """
    # Obtener la URL base del servidor
    load_dotenv()
    base_url_env = os.getenv("API_BASE_URL")
    if base_url_env:
        base_url = base_url_env
    else:
        scheme = "wss" if request.url.scheme == "https" else "ws"
        host = request.url.hostname or "localhost"
        port = request.url.port
        base_url = f"{scheme}://{host}"
        if port:
            base_url += f":{port}"

    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "ws://")
    elif base_url.startswith("https://"):
        base_url = base_url.replace("https://", "wss://")
    elif not base_url.startswith("ws://") and not base_url.startswith("wss://"):
        base_url = f"ws://{base_url}"

    websocket_url = f"{base_url}/ws/ambulancias/{{id_ambulancia}}"

    # Nota: Por ahora no tenemos un manager de conexiones para ambulancias,
    # así que retornamos 0. Esto se puede mejorar en el futuro si se necesita
    # rastrear conexiones activas.
    conexiones_activas = 0

    return WebSocketInfoAmbulanciaResponse(
        websocket_url=websocket_url,
        conexiones_activas=conexiones_activas,
        descripcion=(
            "Endpoint WebSocket para enviar ubicaciones en tiempo real de ambulancias. "
            "Al conectarse con su ID, la ambulancia se marca automáticamente como disponible. "
            "Debe enviar continuamente mensajes JSON con la ubicación. Al desconectar, "
            "la ambulancia se marca automáticamente como no disponible."
        ),
        formato_mensaje={
            "ubicacion": {
                "latitud": 4.7110,
                "longitud": -74.0721
            }
        }
    )

