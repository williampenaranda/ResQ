"""
Router para endpoints de información sobre notificaciones WebSocket para solicitantes.
"""

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv

class WebSocketInfoSolicitanteResponse(BaseModel):
    websocket_url: str = Field(..., description="URL del endpoint WebSocket para conectarse")
    conexiones_activas: int = Field(..., description="Número de solicitantes conectados actualmente")
    descripcion: str = Field(..., description="Descripción del endpoint WebSocket")
    mensaje_bienvenida: dict = Field(..., description="Estructura del mensaje de bienvenida que se recibe al conectar")
    mensaje_solicitud_creada: dict = Field(..., description="Estructura del mensaje que se recibe cuando se crea una solicitud")
    mensaje_operador_asignado: dict = Field(..., description="Estructura del mensaje que se recibe cuando se asigna un operador")
    mensaje_sala_atendida: dict = Field(..., description="Estructura del mensaje que se recibe cuando una sala está atendida")
    mensaje_emergencia_creada: dict = Field(..., description="Estructura del mensaje que se recibe cuando se crea una emergencia")


recibir_notificaciones_router = APIRouter(
    prefix="/recibir-notificaciones",
    tags=["recibir-notificaciones"]
)

@recibir_notificaciones_router.get(
    "/websocket-info",
    response_model=WebSocketInfoSolicitanteResponse,
    summary="Información sobre el WebSocket de solicitantes",
    description=(
        "Proporciona información sobre cómo conectarse al WebSocket para recibir notificaciones "
        "en tiempo real sobre el estado de las solicitudes. Los solicitantes deben conectarse a este endpoint "
        "usando su ID para recibir actualizaciones cuando cambie el estado de su solicitud."
    ),
)
async def obtener_info_websocket_solicitante(request: Request) -> WebSocketInfoSolicitanteResponse:
    """
    Retorna información sobre cómo conectarse al WebSocket de solicitantes.
    
    Este endpoint proporciona:
    - La URL del WebSocket (requiere el ID del solicitante como parámetro)
    - El número de conexiones activas
    - Ejemplos de mensajes que se pueden recibir
    """
    from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import get_manager_solicitantes
    
    manager_solicitantes = get_manager_solicitantes()
    
    # Obtener el número de conexiones activas
    conexiones_activas = manager_solicitantes.get_conexiones_activas_count()
    
    # Construir la URL del WebSocket (asumiendo que se ejecuta en localhost:8000 por defecto)
    # En producción, esto debería venir de una variable de entorno
    load_dotenv()
    import os
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
    
    # La URL incluye el ID del solicitante como parámetro de ruta
    websocket_url_template = f"{base_url}/ws/solicitantes/{{id_solicitante}}"
    
    return WebSocketInfoSolicitanteResponse(
        websocket_url=websocket_url_template,
        conexiones_activas=conexiones_activas,
        descripcion=(
            "Endpoint WebSocket para recibir notificaciones en tiempo real sobre el estado de tus solicitudes. "
            "Al conectarse usando tu ID de solicitante, recibirás un mensaje de bienvenida y luego comenzarás a recibir "
            "notificaciones automáticas sobre: "
            "1) Cuando se crea tu solicitud (tipo: 'solicitud_creada'), "
            "2) Cuando un operador se asigna a tu solicitud (tipo: 'operador_asignado'), "
            "3) Cuando tu sala está atendida (tipo: 'sala_atendida'), "
            "4) Cuando se crea una emergencia asociada a tu solicitud (tipo: 'emergencia_creada')."
        ),
        mensaje_bienvenida={
            "type": "connection",
            "message": "Conectado como solicitante {id_solicitante}! Listo para recibir actualizaciones de tu solicitud",
            "id_solicitante": 1
        },
        mensaje_solicitud_creada={
            "type": "solicitud_creada",
            "data": {
                "id": 1,
                "solicitante": {
                    "id": 1,
                    "nombre": "Juan",
                    "apellido": "Pérez"
                },
                "ubicacion": {
                    "latitud": 4.7110,
                    "longitud": -74.0721
                },
                "fechaHora": "2024-01-15T10:30:00",
                "room": "emergencia-uuid-1234"
            },
            "timestamp": "2024-01-15T10:30:00.123456"
        },
        mensaje_operador_asignado={
            "type": "operador_asignado",
            "data": {
                "room": "emergencia-uuid-1234",
                "operador": {
                    "id": 1,
                    "nombre": "Dr. María",
                    "apellido": "González"
                }
            },
            "timestamp": "2024-01-15T10:35:00.123456"
        },
        mensaje_sala_atendida={
            "type": "sala_atendida",
            "data": {
                "room": "emergencia-uuid-1234",
                "estado": "atendida"
            },
            "timestamp": "2024-01-15T10:35:00.123456"
        },
        mensaje_emergencia_creada={
            "type": "emergencia_creada",
            "data": {
                "id": 1,
                "estado": "PENDIENTE",
                "tipoAmbulancia": "BASICA",
                "nivelPrioridad": "ALTA",
                "descripcion": "Emergencia médica",
                "solicitud_id": 1
            },
            "timestamp": "2024-01-15T10:40:00.123456"
        }
    )

