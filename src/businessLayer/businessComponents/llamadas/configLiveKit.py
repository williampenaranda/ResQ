"""
Módulo de configuración compartida para LiveKit.
Centraliza la carga y validación de las variables de entorno de LiveKit.
"""

import os
from dotenv import load_dotenv
from typing import Optional
from urllib.parse import urlparse, urlunparse

# Cargar variables de entorno
load_dotenv()

# Variables de configuración de LiveKit
LIVEKIT_API_KEY: Optional[str] = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET: Optional[str] = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL: Optional[str] = os.getenv("LIVEKIT_URL")

# Instancia global del cliente de API (singleton pattern)
_livekit_api: Optional[object] = None
_livekit_health_checked: bool = False


def validate_livekit_config() -> None:
    """
    Valida que todas las variables de entorno de LiveKit estén configuradas.
    
    Raises:
        ValueError: Si alguna variable de entorno no está configurada.
    """
    if not LIVEKIT_API_KEY:
        raise ValueError("LIVEKIT_API_KEY no está configurada en las variables de entorno")
    if not LIVEKIT_API_SECRET:
        raise ValueError("LIVEKIT_API_SECRET no está configurada en las variables de entorno")
    if not LIVEKIT_URL:
        raise ValueError("LIVEKIT_URL no está configurada en las variables de entorno")


def get_room_service():
    """
    Obtiene o crea la instancia del cliente de API de LiveKit y retorna el servicio de salas.
    Implementa el patrón singleton para reutilizar la conexión.
    
    Returns:
        Instancia del servicio de salas de LiveKit (accesible a través de .aroom)
        
    Raises:
        ValueError: Si las variables de entorno no están configuradas.
    """
    global _livekit_api
    
    # Importar aquí para evitar problemas de carga circular
    from livekit import api
    
    # Validar configuración antes de crear el servicio
    validate_livekit_config()
    
    if _livekit_api is None:
        # Crear el cliente de API de LiveKit
        _livekit_api = api.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )
    
    # Retornar el cliente completo (el servicio de salas está en .aroom)
    return _livekit_api


async def ensure_livekit_healthcheck(timeout: float = 5.0) -> None:
    """
    Verifica que el servidor de LiveKit esté accesible realizando un healthcheck.
    Se utiliza para comprobar el estado del servicio en el arranque.

    Args:
        timeout: Tiempo máximo en segundos para esperar la respuesta.

    Raises:
        ValueError: Si la configuración de LiveKit no es válida.
        RuntimeError: Si el servidor de LiveKit no responde satisfactoriamente.
    """
    global _livekit_health_checked

    if _livekit_health_checked:
        return

    validate_livekit_config()

    try:
        from aiohttp import ClientSession, TCPConnector, client_exceptions

        parsed = urlparse(LIVEKIT_URL or "")

        scheme = parsed.scheme.lower() if parsed.scheme else ""
        if scheme in ("ws", "wss"):
            scheme = "http" if scheme == "ws" else "https"
        if scheme not in ("http", "https"):
            scheme = "http"

        netloc = parsed.netloc or parsed.path
        if not netloc:
            netloc = "127.0.0.1:7880"

        normalized_base = urlunparse((scheme, netloc, "", "", "", ""))

        async def _check(base_url: str) -> None:
            base_parsed = urlparse(base_url)
            base_scheme = base_parsed.scheme or "http"
            connector = TCPConnector(ssl=False) if base_scheme == "http" else None

            async with ClientSession(connector=connector) as session:
                health_url = f"{base_url.rstrip('/')}/livekit/api/health"
                async with session.get(health_url, timeout=timeout) as response:
                    if response.status == 404:
                        async with session.get(base_url, timeout=timeout) as root_response:
                            if root_response.status != 200:
                                body = await root_response.text()
                                raise RuntimeError(
                                    f"LiveKit base endpoint failed ({root_response.status}): {body}"
                                )
                            body = await root_response.text()
                            if "ok" not in body.lower():
                                raise RuntimeError(
                                    f"LiveKit base endpoint returned unexpected body: {body}"
                                )
                        return

                    if response.status != 200:
                        body = await response.text()
                        raise RuntimeError(
                            f"LiveKit healthcheck failed ({response.status}): {body}"
                        )

                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        data = await response.json()
                        if not data or data.get("status") != "ok":
                            raise RuntimeError(
                                f"LiveKit healthcheck returned unexpected payload: {data}"
                            )
                    else:
                        body = await response.text()
                        if "ok" not in body.lower():
                            raise RuntimeError(
                                f"LiveKit healthcheck returned unexpected body: {body}"
                            )

        try:
            await _check(normalized_base)
        except client_exceptions.ClientConnectorSSLError as ssl_error:
            message = str(ssl_error).upper()
            if "WRONG_VERSION_NUMBER" in message and normalized_base.startswith("https://"):
                fallback_base = normalized_base.replace("https://", "http://", 1)
                await _check(fallback_base)
            else:
                raise
    except Exception as exc:
        raise RuntimeError(f"No se pudo verificar el estado de LiveKit: {exc}") from exc

    _livekit_health_checked = True

