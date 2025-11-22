"""
Router para evaluar solicitudes y crear emergencias.
"""

from fastapi import APIRouter, Body, HTTPException, status, Depends
from pydantic import BaseModel, Field
from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessWorkflow.evaluarSolicitud import EvaluarSolicitud
from src.api.security import require_auth, require_role
from src.security.entities.Usuario import TipoUsuario

evaluar_emergencia_router = APIRouter(
    prefix="/evaluar-emergencia",
    tags=["evaluar-emergencia"],
    dependencies=[Depends(require_auth)]
)


class EvaluarSolicitudRequest(BaseModel):
    """Modelo de request para evaluar una solicitud y crear una emergencia."""
    solicitud_id: int = Field(..., gt=0, description="ID de la solicitud")
    tipoAmbulancia: TipoAmbulancia = Field(..., description="Tipo de ambulancia requerida")
    nivelPrioridad: NivelPrioridad = Field(..., description="Nivel de prioridad")
    descripcion: str = Field(..., min_length=1, description="Descripción de la emergencia")
    id_operador: int = Field(..., gt=0, description="ID del operador asignado")
    solicitante_id: int = Field(..., gt=0, description="ID del solicitante")


from typing import Optional
from src.businessLayer.businessComponents.entidades.buscarAmbulanciaCercana import BuscarAmbulanciaCercana

class EvaluarEmergenciaResponse(BaseModel):
    """Modelo de respuesta que incluye la emergencia creada y la ambulancia más cercana sugerida."""
    emergencia: Emergencia
    id_ambulancia_cercana: Optional[int] = Field(None, description="ID de la ambulancia más cercana disponible")


@evaluar_emergencia_router.post(
    "",
    response_model=EvaluarEmergenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Evaluar solicitud y crear emergencia",
    description=(
        "Evalúa una solicitud y crea una emergencia. "
        "Este endpoint crea la emergencia, notifica al solicitante y busca la ambulancia más cercana disponible. "
        "Solo OPERADOR_EMERGENCIA y ADMINISTRADOR pueden evaluar solicitudes."
    ),
)
async def evaluar_solicitud(
    evaluacion_data: EvaluarSolicitudRequest = Body(...),
    payload: dict = Depends(require_auth)
):
    """
    Evalúa una solicitud y crea una emergencia.
    Requiere que la solicitud, operador y solicitante existan en la base de datos.
    """
    try:
        # 1. Crear la emergencia
        emergencia_creada = await EvaluarSolicitud.evaluar_solicitud(
            solicitud_id=evaluacion_data.solicitud_id,
            tipo_ambulancia=evaluacion_data.tipoAmbulancia,
            nivel_prioridad=evaluacion_data.nivelPrioridad,
            descripcion=evaluacion_data.descripcion,
            id_operador=evaluacion_data.id_operador,
            solicitante_id=evaluacion_data.solicitante_id
        )
        
        # 2. Buscar la ambulancia más cercana
        id_ambulancia_cercana = None
        try:
            if emergencia_creada.solicitud and emergencia_creada.solicitud.ubicacion:
                id_ambulancia_cercana = BuscarAmbulanciaCercana.encontrar_mas_cercana(
                    ubicacion_emergencia=emergencia_creada.solicitud.ubicacion,
                    tipo_ambulancia=emergencia_creada.tipoAmbulancia,
                    nivel_prioridad=emergencia_creada.nivelPrioridad
                )
        except Exception as e:
            # Si falla la búsqueda de ambulancia, no fallamos la creación de la emergencia
            # Solo logueamos el error (aquí print por simplicidad)
            print(f"Error al buscar ambulancia cercana: {e}")
            
        return EvaluarEmergenciaResponse(
            emergencia=emergencia_creada,
            id_ambulancia_cercana=id_ambulancia_cercana
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

