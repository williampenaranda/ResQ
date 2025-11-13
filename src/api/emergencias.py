from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.businessLayer.businessWorkflow.solicitarAmbulancia import SolicitarAmbulancia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento

emergencias_router = APIRouter(
    prefix="/emergencias",
    tags=["emergencias"]
)

# ======== Modelos de Request/Response para la API (no exponen entidades internas) ========

class SolicitanteRequest(BaseModel):
    id: int = Field(..., description="ID del solicitante en el sistema")
    nombre: str = Field(..., min_length=1, description="Primer nombre")
    apellido: str = Field(..., min_length=1, description="Primer apellido")
    fechaNacimiento: datetime = Field(..., description="Fecha de nacimiento")
    documento: str = Field(..., min_length=1, description="Documento")
    tipoDocumento: TipoDocumento = Field(..., description="Tipo de documento")
    numeroDocumento: str = Field(..., min_length=1, description="Número de documento")
    nombre2: Optional[str] = Field(None, description="Segundo nombre")
    apellido2: Optional[str] = Field(None, description="Segundo apellido")
    padecimientos: Optional[List[str]] = Field(default_factory=list, description="Lista de padecimientos relevantes")

class UbicacionRequest(BaseModel):
    latitud: float = Field(..., ge=-90, le=90, description="Latitud GPS")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud GPS")
    fechaHora: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha/hora de captura")

class SolicitudRequest(BaseModel):
    solicitante: SolicitanteRequest = Field(..., description="Datos del solicitante")
    ubicacion: UbicacionRequest = Field(..., description="Ubicación del incidente")
    fechaHora: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha/hora de la solicitud")

class SolicitarAmbulanciaResponse(BaseModel):
    room: str = Field(..., description="Nombre de la sala creada/asignada en LiveKit")
    token: str = Field(..., description="Token JWT de LiveKit para unirse a la sala")
    identity: str = Field(..., description="Identidad generada para el participante")
    server_url: str = Field(..., description="URL del servidor de LiveKit")

class ErrorResponse(BaseModel):
    detail: str

class WebSocketInfoResponse(BaseModel):
    websocket_url: str = Field(..., description="URL del endpoint WebSocket para conectarse")
    conexiones_activas: int = Field(..., description="Número de operadores conectados actualmente")
    descripcion: str = Field(..., description="Descripción del endpoint WebSocket")
    mensaje_bienvenida: dict = Field(..., description="Estructura del mensaje de bienvenida que se recibe al conectar")
    mensaje_emergencia: dict = Field(..., description="Estructura del mensaje que se recibe cuando hay una nueva emergencia")
    ejemplo_conexion: dict = Field(..., description="Ejemplo de cómo conectarse desde JavaScript")

# ======== Endpoints ========

@emergencias_router.get(
    "/websocket-info",
    response_model=WebSocketInfoResponse,
    summary="Información sobre el WebSocket de emergencias",
    description=(
        "Proporciona información sobre cómo conectarse al WebSocket para recibir notificaciones "
        "de nuevas emergencias en tiempo real. Los operadores deben conectarse a este endpoint "
        "para recibir alertas cuando se registre una nueva solicitud de ambulancia."
    ),
)
async def obtener_info_websocket() -> WebSocketInfoResponse:
    """
    Retorna información sobre cómo conectarse al WebSocket de emergencias.
    
    Este endpoint proporciona:
    - La URL del WebSocket
    - El número de conexiones activas
    - Ejemplos de mensajes
    - Ejemplo de código para conectarse
    """
    from src.api.websocket import manager_emergencias
    
    # Obtener el número de conexiones activas
    conexiones_activas = manager_emergencias.get_active_connections_count()
    
    # Construir la URL del WebSocket (asumiendo que se ejecuta en localhost:8000 por defecto)
    # En producción, esto debería venir de una variable de entorno
    import os
    base_url = os.getenv("API_BASE_URL", "ws://localhost:8000")
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "ws://")
    elif base_url.startswith("https://"):
        base_url = base_url.replace("https://", "wss://")
    elif not base_url.startswith("ws://") and not base_url.startswith("wss://"):
        base_url = f"ws://{base_url}"
    
    websocket_url = f"{base_url}/ws/emergencias"
    
    return WebSocketInfoResponse(
        websocket_url=websocket_url,
        conexiones_activas=conexiones_activas,
        descripcion=(
            "Endpoint WebSocket para recibir notificaciones en tiempo real de nuevas emergencias. "
            "Al conectarse, recibirás un mensaje de bienvenida y luego comenzarás a recibir "
            "notificaciones automáticas cuando se registre una nueva solicitud de ambulancia."
        ),
        mensaje_bienvenida={
            "type": "connection",
            "message": "Conectado! listo para recibir emergencias"
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
                "room": "emergencia-uuid-1234",
                "server_url": "wss://livekit.example.com"
            },
            "timestamp": "2024-01-15T10:30:00.123456"
        },
        ejemplo_conexion={
            "javascript": """
// Ejemplo de conexión desde JavaScript
const ws = new WebSocket('ws://localhost:8000/ws/emergencias');

ws.onopen = () => {
    console.log('Conectado al WebSocket de emergencias');
};

ws.onmessage = (event) => {
    const mensaje = JSON.parse(event.data);
    
    if (mensaje.type === 'connection') {
        console.log('Conexión establecida:', mensaje.message);
    } else if (mensaje.type === 'nueva_solicitud') {
        console.log('Nueva emergencia recibida:', mensaje.data);
        // Procesar la nueva emergencia aquí
    }
};

ws.onerror = (error) => {
    console.error('Error en WebSocket:', error);
};

ws.onclose = () => {
    console.log('Conexión cerrada');
};
            """,
            "python": """
# Ejemplo de conexión desde Python
import asyncio
import websockets
import json

async def escuchar_emergencias():
    uri = "ws://localhost:8000/ws/emergencias"
    async with websockets.connect(uri) as websocket:
        # Recibir mensaje de bienvenida
        mensaje = await websocket.recv()
        print("Mensaje recibido:", json.loads(mensaje))
        
        # Escuchar nuevas emergencias
        async for mensaje in websocket:
            data = json.loads(mensaje)
            if data.get("type") == "nueva_solicitud":
                print("Nueva emergencia:", data["data"])

asyncio.run(escuchar_emergencias())
            """
        }
    )

@emergencias_router.post(
    "/solicitar-ambulancia",
    response_model=SolicitarAmbulanciaResponse,
    responses={
        200: {"description": "Solicitud procesada exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos de entrada inválidos"},
        500: {"model": ErrorResponse, "description": "Error interno al procesar la solicitud"},
    },
    summary="Solicitar una ambulancia",
    description=(
        "Crea una sala de LiveKit para la emergencia, genera identidad y token para el solicitante, "
        "y retorna la información necesaria para unirse a la llamada. "
        "La identidad del participante y el nombre de la sala se generan automáticamente."
    ),
)
async def solicitar_ambulancia(
    solicitud: SolicitudRequest = Body(
        ...,
        examples={
            "ejemploBasico": {
                "summary": "Solicitud mínima",
                "value": {
                    "solicitante": {
                        "id": 1,
                        "nombre": "Juan",
                        "apellido": "Pérez",
                        "fechaNacimiento": "1990-05-10",
                        "tipoDocumento": "CC",
                        "numeroDocumento": "1234567890",
                        "padecimientos": ["hipertensión"]
                    },
                    "ubicacion": {
                        "latitud": 4.7110,
                        "longitud": -74.0721
                    }
                }
            }
        }
    )
) -> SolicitarAmbulanciaResponse:
    """
    Procesa la solicitud de ambulancia y retorna credenciales para la llamada en LiveKit.
    """
    try:
        # Adaptación mínima al workflow interno:
        # El workflow espera un objeto `Solicitud` interno; aquí usamos el request API:
        from src.businessLayer.businessEntities.solicitante import Solicitante
        from src.businessLayer.businessEntities.ubicacion import Ubicacion
        from src.businessLayer.businessEntities.solicitud import Solicitud

        solicitante_be = Solicitante(**solicitud.solicitante.model_dump())
        ubicacion_be = Ubicacion(**solicitud.ubicacion.model_dump())
        solicitud_be = Solicitud(
            id=solicitud.solicitante.id,  # o un ID temporal si aplica
            solicitante=solicitante_be,
            fechaHora=solicitud.fechaHora or datetime.utcnow(),
            ubicacion=ubicacion_be,
        )

        result = await SolicitarAmbulancia.registrarSolicitud(solicitud_be)

        # Notificar a todos los clientes conectados vía WebSocket
        from src.api.websocket import notificar_nueva_solicitud
        
        # Preparar datos de la solicitud para notificar
        solicitud_notificacion = {
            "solicitante": {
                "id": solicitud.solicitante.id,
                "nombre": solicitud.solicitante.nombre,
                "apellido": solicitud.solicitante.apellido,
                "tipoDocumento": solicitud.solicitante.tipoDocumento.value if hasattr(solicitud.solicitante.tipoDocumento, 'value') else str(solicitud.solicitante.tipoDocumento),
                "numeroDocumento": solicitud.solicitante.numeroDocumento,
                "padecimientos": solicitud.solicitante.padecimientos or []
            },
            "ubicacion": {
                "latitud": solicitud.ubicacion.latitud,
                "longitud": solicitud.ubicacion.longitud,
                "fechaHora": solicitud.ubicacion.fechaHora.isoformat() if solicitud.ubicacion.fechaHora else None
            },
            "fechaHora": (solicitud.fechaHora or datetime.utcnow()).isoformat(),
            "room": result["room"],
            "server_url": result["server_url"]
        }
        
        # Notificar de forma asíncrona (no bloquea la respuesta)
        await notificar_nueva_solicitud(solicitud_notificacion)

        return SolicitarAmbulanciaResponse(**result)

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))