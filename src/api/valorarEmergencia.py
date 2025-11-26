"""
Router para valorar solicitudes y crear emergencias.
"""

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field
from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessWorkflow.valorarSolicitud import ValorarSolicitud
from typing import Optional
from src.businessLayer.businessComponents.entidades.buscarAmbulanciaCercana import BuscarAmbulanciaCercana
from src.businessLayer.businessComponents.notificaciones.gestorTareasAmbulancias import (
    iniciar_envio_ambulancias,
)

valorar_emergencia_router = APIRouter(
    prefix="/valorar-emergencia",
    tags=["valorar-emergencia"],
)


class ValorarSolicitudRequest(BaseModel):
    """Modelo de request para valorar una solicitud y crear una emergencia."""
    solicitud_id: int = Field(..., gt=0, description="ID de la solicitud")
    tipoAmbulancia: TipoAmbulancia = Field(..., description="Tipo de ambulancia requerida")
    nivelPrioridad: NivelPrioridad = Field(..., description="Nivel de prioridad")
    descripcion: str = Field(..., min_length=1, description="Descripción de la emergencia")
    id_operador: int = Field(..., gt=0, description="ID del operador asignado")
    solicitante_id: int = Field(..., gt=0, description="ID del solicitante")


class ValorarEmergenciaResponse(BaseModel):
    """Modelo de respuesta que incluye la emergencia creada y la ambulancia más cercana sugerida."""
    emergencia: Emergencia
    id_ambulancia_cercana: Optional[int] = Field(None, description="ID de la ambulancia más cercana disponible")


@valorar_emergencia_router.post(
    "",
    response_model=ValorarEmergenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Valorar solicitud y crear emergencia",
    description=(
        "Valora una solicitud y crea una emergencia. "
        "Este endpoint crea la emergencia, notifica al solicitante y busca la ambulancia más cercana disponible."
    ),
)
async def valorar_solicitud(
    valoracion_data: ValorarSolicitudRequest = Body(...)
):
    """
    Valora una solicitud y crea una emergencia.
    Requiere que la solicitud, operador y solicitante existan en la base de datos.
    """
    try:
        # 1. Crear la emergencia
        emergencia_creada = await ValorarSolicitud.valorar_solicitud(
            solicitud_id=valoracion_data.solicitud_id,
            tipo_ambulancia=valoracion_data.tipoAmbulancia,
            nivel_prioridad=valoracion_data.nivelPrioridad,
            descripcion=valoracion_data.descripcion,
            id_operador=valoracion_data.id_operador,
            solicitante_id=valoracion_data.solicitante_id
        )
        
        # 2. Buscar la ambulancia más cercana (solo una vez)
        id_ambulancia_cercana = None
        try:
            if emergencia_creada.solicitud and emergencia_creada.solicitud.ubicacion:
                id_ambulancia_cercana = BuscarAmbulanciaCercana.encontrar_mas_cercana(
                    ubicacion_emergencia=emergencia_creada.solicitud.ubicacion,
                    tipo_ambulancia=emergencia_creada.tipoAmbulancia,
                    nivel_prioridad=emergencia_creada.nivelPrioridad
                )
        except Exception as e:
            # Si falla la búsqueda de ambulancia, no fallamos la creación de la emergencia.
            # Solo logueamos el error (aquí print por simplicidad).
            print(f"Error al buscar ambulancia cercana: {e}")

        # 3. Iniciar el envío periódico de la ubicación de la ambulancia óptima al operador
        #    (solo si se encontró una ambulancia y hay operador asociado)
        try:
            if (
                id_ambulancia_cercana is not None
                and emergencia_creada.id is not None
                and valoracion_data.id_operador is not None
            ):
                print(f"[INFO] Iniciando envio de ubicacion: operador={valoracion_data.id_operador}, emergencia={emergencia_creada.id}, ambulancia={id_ambulancia_cercana}")
                resultado = iniciar_envio_ambulancias(
                    id_operador=valoracion_data.id_operador,
                    emergencia_id=emergencia_creada.id,
                    id_ambulancia=id_ambulancia_cercana,
                )
                if resultado:
                    print(f"[OK] Envio de ubicacion iniciado correctamente para emergencia {emergencia_creada.id}")
                else:
                    print(f"[WARN] No se pudo iniciar envio de ubicacion (ya existe tarea para emergencia {emergencia_creada.id})")
            else:
                print(f"[WARN] No se puede iniciar envio de ubicacion: id_ambulancia={id_ambulancia_cercana}, emergencia_id={emergencia_creada.id}, id_operador={valoracion_data.id_operador}")
        except Exception as e:
            # Si falla el inicio del envío periódico, no rompemos el flujo principal.
            print(
                f"[ERROR] Error al iniciar envío de ubicación de ambulancia óptima "
                f"(emergencia {emergencia_creada.id}, ambulancia {id_ambulancia_cercana}): {e}"
            )
            import traceback
            traceback.print_exc()
            
        return ValorarEmergenciaResponse(
            emergencia=emergencia_creada,
            id_ambulancia_cercana=id_ambulancia_cercana
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
