from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.businessLayer.businessWorkflow.solicitarAmbulancia import SolicitarAmbulancia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from dotenv import load_dotenv

class WebSocketInfoResponse(BaseModel):
    websocket_url: str = Field(..., description="URL del endpoint WebSocket para conectarse")
    conexiones_activas: int = Field(..., description="Número de operadores conectados actualmente")
    descripcion: str = Field(..., description="Descripción del endpoint WebSocket")
    mensaje_bienvenida: dict = Field(..., description="Estructura del mensaje de bienvenida que se recibe al conectar")
    mensaje_emergencia: dict = Field(..., description="Estructura del mensaje que se recibe cuando hay una nueva emergencia")
    mensaje_sala_atendida: dict = Field(..., description="Estructura del mensaje que se recibe cuando una sala está atendida")
    mensaje_info_ambulancias: dict = Field(..., description="Estructura del mensaje que se recibe con información de ambulancias durante la evaluación")


atender_emergencias_router = APIRouter(
    prefix="/atender-emergencias",
    tags=["atender-emergencias"]
)

@atender_emergencias_router.get(
    "/websocket-info",
    response_model=WebSocketInfoResponse,
    summary="Información sobre el WebSocket de emergencias",
    description=(
        "Proporciona información sobre cómo conectarse al WebSocket para recibir notificaciones "
        "de nuevas emergencias en tiempo real. Los operadores deben conectarse a este endpoint "
        "para recibir alertas cuando se registre una nueva solicitud de ambulancia. "
        "Si se proporciona el parámetro id_operador en la URL, recibirás información de ambulancias "
        "cada segundo cuando estés evaluando una emergencia."
    ),
)
async def obtener_info_websocket(request: Request) -> WebSocketInfoResponse:
    """
    Retorna información sobre cómo conectarse al WebSocket de emergencias.
    
    Este endpoint proporciona:
    - La URL del WebSocket (con parámetro opcional id_operador)
    - El número de conexiones activas
    - Ejemplos de mensajes
    - Ejemplo de código para conectarse
    """
    from src.businessLayer.businessComponents.notificaciones.notificadorOperadorEmergencias import get_manager_operadores_emergencia
    
    manager_operadores_emergencia = get_manager_operadores_emergencia()
    
    # Obtener el número de conexiones activas
    conexiones_activas = manager_operadores_emergencia.get_conexiones_activas_count()
    
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
    
    websocket_url = f"{base_url}/ws/operadores-emergencia"
    
    return WebSocketInfoResponse(
        websocket_url=websocket_url,
        conexiones_activas=conexiones_activas,
        descripcion=(
            "Endpoint WebSocket para recibir notificaciones en tiempo real de emergencias. "
            "Al conectarse, recibirás un mensaje de bienvenida y luego comenzarás a recibir "
            "notificaciones automáticas de: "
            "1) Nuevas solicitudes de ambulancia (tipo: 'nueva_solicitud') con el nombre de la sala, "
            "2) Salas atendidas cuando se llenan (tipo: 'sala_atendida') con el nombre de la sala + 'atendida', "
            "3) Información de ambulancias (tipo: 'info_ambulancias') cada segundo cuando estés evaluando una emergencia "
            "(requiere conectarse con el parámetro id_operador en la URL)."
        ),
        mensaje_bienvenida={
            "type": "connection",
            "message": "Conectado como operador 1! listo para recibir nuevas solicitudes",
            "id_operador": 1
        },
        mensaje_emergencia={
            "type": "nueva_solicitud",
            "data": {
                "solicitante": {
                    "id": 1,
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "tipoDocumento": "CC",
                    "numeroDocumento": "1234567890",
                    "padecimientos": ["hipertensión"]
                },
                "ubicacion": {
                    "latitud": 4.7110,
                    "longitud": -74.0721,
                    "fechaHora": "2024-01-15T10:30:00"
                },
                "fechaHora": "2024-01-15T10:30:00",
                "room": "emergencia-uuid-1234"
            },
            "timestamp": "2024-01-15T10:30:00.123456"
        },
        mensaje_sala_atendida={
            "type": "sala_atendida",
            "data": {
                "room": "emergencia-uuid-1234",
                "estado": "atendida"
            },
            "timestamp": "2024-01-15T10:30:00.123456"
        },
        mensaje_info_ambulancias={
            "type": "info_ambulancias",
            "emergencia_id": 123,
            "ambulancias": [
                {
                    "id": 1,
                    "latitud": 4.7110,
                    "longitud": -74.0721
                },
                {
                    "id": 2,
                    "latitud": 4.7120,
                    "longitud": -74.0730
                }
            ],
            "timestamp": 1234567890.123
        }
    )
