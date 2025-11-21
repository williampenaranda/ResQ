from fastapi import APIRouter, Body, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from src.businessLayer.businessWorkflow.solicitarAmbulancia import SolicitarAmbulancia
from src.api.security import require_auth

solicitudes_router = APIRouter(
    prefix="/solicitudes",
    tags=["solicitudes"],
    dependencies=[Depends(require_auth)]
)


class UbicacionRequest(BaseModel):
    latitud: float = Field(..., ge=-90, le=90, description="Latitud GPS")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud GPS")

class SolicitudRequest(BaseModel):
    id_solicitante: int = Field(..., gt=0, description="ID del solicitante en el sistema")
    ubicacion: UbicacionRequest = Field(..., description="Ubicación del incidente")

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
        "El solicitante se obtiene desde la base de datos usando el ID proporcionado. "
        "La fecha/hora de la solicitud y ubicación se generan automáticamente."
    ),
)
async def solicitar_ambulancia(
    solicitud: SolicitudRequest = Body(
        ...,
        examples={
            "ejemploBasico": {
                "summary": "Solicitud mínima",
                "value": {
                    "id_solicitante": 1,
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
    
    El backend gestiona automáticamente:
    - Obtención del solicitante desde la base de datos
    - Creación de la ubicación con fecha/hora actual
    - Creación de la solicitud con fecha/hora actual
    """
    try:
        from src.businessLayer.businessComponents.entidades.servicioSolicitante import ServicioSolicitante
        from src.businessLayer.businessEntities.ubicacion import Ubicacion
        from src.businessLayer.businessEntities.solicitud import Solicitud

        # Obtener el solicitante desde la base de datos
        solicitante = ServicioSolicitante.obtener_por_id(solicitud.id_solicitante)
        if not solicitante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitante con ID {solicitud.id_solicitante} no encontrado"
            )

        # Crear la ubicación con fecha/hora actual
        fecha_hora_actual = datetime.utcnow()
        ubicacion_be = Ubicacion(
            id=None,
            latitud=solicitud.ubicacion.latitud,
            longitud=solicitud.ubicacion.longitud,
            fechaHora=fecha_hora_actual
        )

        # Crear la solicitud con fecha/hora actual
        solicitud_be = Solicitud(
            id=None,
            solicitante=solicitante,
            fechaHora=fecha_hora_actual,
            ubicacion=ubicacion_be
        )

        # Procesar la solicitud a través del workflow
        result = await SolicitarAmbulancia.registrarSolicitud(solicitud_be)

        return SolicitarAmbulanciaResponse(**result)

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

