from fastapi import APIRouter, Body, HTTPException, status, Query, Path, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.businessLayer.businessWorkflow.solicitarAmbulancia import SolicitarAmbulancia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessComponents.entidades.servicioEmergencia import ServicioEmergencia
from src.api.security import require_auth, require_role
from src.security.entities.Usuario import TipoUsuario
from src.businessLayer.businessComponents.notificaciones.notificadorSolicitante import notificar_emergencia_evaluada

emergencias_router = APIRouter(
    prefix="/emergencias",
    tags=["emergencias"],
    dependencies=[Depends(require_auth)]
)

# ======== Modelos para CRUD de Emergencias ========

class EmergenciaCreate(BaseModel):
    """Modelo de request para crear una emergencia."""
    solicitud_id: int = Field(..., gt=0, description="ID de la solicitud")
    estado: EstadoEmergencia = Field(..., description="Estado de la emergencia")
    tipoAmbulancia: TipoAmbulancia = Field(..., description="Tipo de ambulancia requerida")
    nivelPrioridad: NivelPrioridad = Field(..., description="Nivel de prioridad")
    descripcion: str = Field(..., min_length=1, description="Descripción de la emergencia")
    id_operador: int = Field(..., gt=0, description="ID del operador asignado")
    solicitante_id: int = Field(..., gt=0, description="ID del solicitante")


class EmergenciaUpdate(BaseModel):
    """Modelo de request para actualizar una emergencia."""
    estado: Optional[EstadoEmergencia] = Field(None, description="Estado de la emergencia")
    tipoAmbulancia: Optional[TipoAmbulancia] = Field(None, description="Tipo de ambulancia requerida")
    nivelPrioridad: Optional[NivelPrioridad] = Field(None, description="Nivel de prioridad")
    descripcion: Optional[str] = Field(None, min_length=1, description="Descripción de la emergencia")
    id_operador: Optional[int] = Field(None, gt=0, description="ID del operador asignado")
    solicitud_id: Optional[int] = Field(None, gt=0, description="ID de la solicitud")
    solicitante_id: Optional[int] = Field(None, gt=0, description="ID del solicitante")


# ======== Endpoints CRUD ========
# IMPORTANTE: Las rutas específicas deben ir ANTES de las rutas con parámetros dinámicos

@emergencias_router.get(
    "/por-estado/{estado}",
    response_model=List[Emergencia],
    summary="Listar emergencias por estado",
    description="Lista emergencias filtradas por estado.",
    dependencies=[Depends(require_auth)],
)
def listar_emergencias_por_estado(
    estado: EstadoEmergencia = Path(..., description="Estado de la emergencia"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir"),
):
    """
    Lista emergencias filtradas por estado.
    """
    try:
        return ServicioEmergencia.obtener_por_estado(estado, limit=limit, offset=offset)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.get(
    "/por-operador/{id_operador}",
    response_model=List[Emergencia],
    summary="Listar emergencias por operador",
    description="Lista emergencias asignadas a un operador específico.",
    dependencies=[Depends(require_auth)],
)
def listar_emergencias_por_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir"),
):
    """
    Lista emergencias asignadas a un operador específico.
    """
    try:
        return ServicioEmergencia.obtener_por_operador(id_operador, limit=limit, offset=offset)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.get(
    "/por-solicitante/{id_solicitante}",
    response_model=List[Emergencia],
    summary="Listar emergencias por solicitante",
    description="Lista emergencias realizadas por un solicitante específico.",
    dependencies=[Depends(require_auth)],
)
def listar_emergencias_por_solicitante(
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir"),
):
    """
    Lista emergencias realizadas por un solicitante específico.
    """
    try:
        return ServicioEmergencia.obtener_por_solicitante(id_solicitante, limit=limit, offset=offset)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.get(
    "/por-solicitud/{id_solicitud}",
    response_model=Emergencia,
    summary="Obtener emergencia por solicitud",
    description="Obtiene la emergencia asociada a una solicitud específica.",
    dependencies=[Depends(require_auth)],
)
def obtener_emergencia_por_solicitud(
    id_solicitud: int = Path(..., gt=0, description="ID de la solicitud"),
):
    """
    Obtiene la emergencia asociada a una solicitud específica.
    """
    try:
        encontrada = ServicioEmergencia.obtener_por_solicitud(id_solicitud)
        if not encontrada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergencia no encontrada para esta solicitud")
        return encontrada
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.post(
    "",
    response_model=Emergencia,
    status_code=status.HTTP_201_CREATED,
    summary="Crear emergencia",
    description="Crea una nueva emergencia y retorna el recurso creado con su ID asignado. Solo OPERADOR_EMERGENCIA y ADMINISTRADOR pueden crear emergencias.",
)
async def crear_emergencia(
    emergencia_data: EmergenciaCreate = Body(...),
    payload: dict = Depends(require_auth)
):
    """
    Crea una nueva emergencia.
    Requiere que la solicitud, operador y solicitante existan en la base de datos.
    """
    try:
        from src.dataLayer.dataAccesComponets.repositorioSolicitudes import obtener_solicitud_por_id
        from src.dataLayer.dataAccesComponets.repositorioSolicitantes import obtener_solicitante_por_id
        
        # Obtener la solicitud
        solicitud = obtener_solicitud_por_id(emergencia_data.solicitud_id)
        if not solicitud:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con id {emergencia_data.solicitud_id} no encontrada"
            )
        
        # Obtener el solicitante
        solicitante = obtener_solicitante_por_id(emergencia_data.solicitante_id)
        if not solicitante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitante con id {emergencia_data.solicitante_id} no encontrado"
            )
        
        # Crear la entidad Emergencia
        emergencia = Emergencia(
            id=None,
            solicitud=solicitud,
            estado=emergencia_data.estado,
            tipoAmbulancia=emergencia_data.tipoAmbulancia,
            nivelPrioridad=emergencia_data.nivelPrioridad,
            descripcion=emergencia_data.descripcion,
            id_operador=emergencia_data.id_operador,
            solicitante=solicitante
        )
        
        creada = ServicioEmergencia.crear(emergencia)
        if creada is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error al crear la emergencia. Verifique que todos los IDs sean válidos."
            )
        
        # Notificar a los solicitantes sobre la nueva emergencia
        # Usar mode='json' para convertir date/datetime a strings serializables
        await notificar_emergencia_evaluada(creada.solicitante.id, creada.model_dump(mode='json'))
        
        return creada
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.get(
    "",
    response_model=List[Emergencia],
    summary="Listar emergencias",
    description="Lista todas las emergencias con paginación.",
    dependencies=[Depends(require_auth)],
)
def listar_emergencias(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir"),
):
    """
    Lista emergencias con paginación.
    """
    try:
        return ServicioEmergencia.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.get(
    "/{id_emergencia}",
    response_model=Emergencia,
    summary="Obtener emergencia por ID",
    description="Obtiene una emergencia específica por su ID.",
    dependencies=[Depends(require_auth)],
)
def obtener_emergencia(
    id_emergencia: int = Path(..., gt=0, description="ID de la emergencia"),
):
    """
    Obtiene una emergencia por su ID.
    """
    try:
        encontrada = ServicioEmergencia.obtener_por_id(id_emergencia)
        if not encontrada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergencia no encontrada")
        return encontrada
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.put(
    "/{id_emergencia}",
    response_model=Emergencia,
    summary="Actualizar emergencia",
    description="Actualiza una emergencia existente.",
    dependencies=[Depends(require_auth)],
)
def actualizar_emergencia(
    id_emergencia: int = Path(..., gt=0, description="ID de la emergencia"),
    cambios: EmergenciaUpdate = Body(...),
):
    """
    Actualiza una emergencia existente.
    Solo se actualizan los campos proporcionados en el body.
    """
    try:
        # Filtrar campos None del body
        cambios_dict = {k: v for k, v in cambios.model_dump().items() if v is not None}
        
        if not cambios_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos un campo para actualizar"
            )
        
        actualizada = ServicioEmergencia.actualizar(id_emergencia, cambios_dict)
        if not actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergencia no encontrada")
        return actualizada
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emergencias_router.delete(
    "/{id_emergencia}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar emergencia",
    description="Elimina una emergencia por su ID.",
    dependencies=[Depends(require_auth)],
)
def eliminar_emergencia(
    id_emergencia: int = Path(..., gt=0, description="ID de la emergencia"),
):
    """
    Elimina una emergencia por su ID.
    """
    try:
        eliminada = ServicioEmergencia.eliminar(id_emergencia)
        if not eliminada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergencia no encontrada")
        return None
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))