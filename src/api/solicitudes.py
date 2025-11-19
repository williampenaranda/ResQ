from fastapi import APIRouter, Body, HTTPException, status, Query, Path, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.businessLayer.businessWorkflow.solicitarAmbulancia import SolicitarAmbulancia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.api.security import require_auth

solicitudes_router = APIRouter(
    prefix="/solicitudes",
    tags=["solicitudes"],
    dependencies=[Depends(require_auth)]
)


class SolicitanteRequest(BaseModel):
    id: int = Field(..., description="ID del solicitante en el sistema")
    nombre: str = Field(..., min_length=1, description="Primer nombre")
    apellido: str = Field(..., min_length=1, description="Primer apellido")
    fechaNacimiento: datetime = Field(..., description="Fecha de nacimiento")
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

# ======== Endpoints ========
@solicitudes_router.post(
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

        solicitante_be = Solicitante.model_validate(
            solicitud.solicitante.model_dump() if hasattr(solicitud.solicitante, "model_dump") else solicitud.solicitante
        )
        ubicacion_be = Ubicacion.model_validate(
            solicitud.ubicacion.model_dump() if hasattr(solicitud.ubicacion, "model_dump") else solicitud.ubicacion
        )
        solicitante_id = (
            getattr(solicitud.solicitante, "id", None)
            if not isinstance(solicitud.solicitante, dict)
            else solicitud.solicitante.get("id")
        )

        solicitud_be = Solicitud(
            id=solicitante_id or solicitante_be.id,
            solicitante=solicitante_be,
            fechaHora=solicitud.fechaHora or datetime.utcnow(),
            ubicacion=ubicacion_be,
        )

        result = await SolicitarAmbulancia.registrarSolicitud(solicitud_be.model_dump(mode="json"))

        # La notificación se hace dentro del workflow SolicitarAmbulancia
        # No es necesario notificar aquí, ya se hace en el workflow

        return SolicitarAmbulanciaResponse(**result)

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

