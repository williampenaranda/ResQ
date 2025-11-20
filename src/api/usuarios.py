from fastapi import APIRouter, HTTPException, status, Body, Path, Query, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from src.security.entities.Usuario import Usuario, TipoUsuario
from src.dataLayer.dataAccesComponets.repositorioUsuarios import (
    crearUsuario,
    obtener_usuario_por_id,
    listar_usuarios,
    actualizar_usuario,
    eliminar_usuario,
    actualizarUsuarioPersona,
    obtener_id_persona_por_credenciales
)
from src.api.security import require_role

usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)





class IdPersonaResponse(BaseModel):
    """Modelo de respuesta con el id_persona."""
    id_persona: Optional[int] = Field(None, description="ID de la persona asociada al usuario")


class UsuarioCreate(BaseModel):
    """Modelo de request para crear un usuario (sin id, id_persona ni tipoUsuario)."""
    nombreDeUsuario: str = Field(..., min_length=1)
    email: EmailStr
    contrasenaHasheada: str = Field(..., min_length=1)

@usuarios_router.post(
    "",
    response_model=Usuario,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario y retorna el usuario creado con su ID asignado. id_persona y tipoUsuario serán null."
)
async def crear_usuario(usuario_data: UsuarioCreate = Body(...)):
    try:
        # Convertir el modelo de request a Usuario (sin id, id_persona y tipoUsuario)
        usuario = Usuario(
            id=None,
            nombreDeUsuario=usuario_data.nombreDeUsuario,
            email=usuario_data.email,
            contrasenaHasheada=usuario_data.contrasenaHasheada,
            id_persona=None,
            tipoUsuario=None
        )
        nuevo_usuario = crearUsuario(usuario)
        if not nuevo_usuario:
            # Conflicto: usuario/email duplicado
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuario o email ya existente"
            )
        return nuevo_usuario
    except ValueError as ve:
        # Datos inválidos
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Error interno
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@usuarios_router.get(
    "/{id_usuario}",
    response_model=Usuario,
    summary="Obtener usuario por ID",
    description="Obtiene un usuario por su ID."
)
async def obtener_usuario(
    id_usuario: int = Path(..., gt=0, description="ID del usuario")
):
    try:
        encontrado = obtener_usuario_por_id(id_usuario)
        if not encontrado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return encontrado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@usuarios_router.get(
    "",
    response_model=List[Usuario],
    summary="Listar usuarios",
    description="Lista usuarios con paginación."
    #dependencies=[Depends(require_role(TipoUsuario.ADMINISTRADOR))]
)
async def listar_usuarios_endpoint(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación")
):
    try:
        return listar_usuarios(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@usuarios_router.put(
    "/{id_usuario}",
    response_model=Usuario,
    summary="Actualizar usuario",
    description="Actualiza campos del usuario y retorna el usuario actualizado."
)
async def actualizar_usuario_endpoint(
    id_usuario: int = Path(..., gt=0, description="ID del usuario"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar")
):
    try:
        actualizado = actualizar_usuario(id_usuario, cambios)
        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o conflicto de datos"
            )
        return actualizado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@usuarios_router.delete(
    "/{id_usuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario por ID. No retorna contenido."
)
async def eliminar_usuario_endpoint(
    id_usuario: int = Path(..., gt=0, description="ID del usuario")
):
    try:
        ok = eliminar_usuario(id_usuario)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class CredencialesRequest(BaseModel):
    """Modelo de request para obtener id_persona por credenciales."""
    email: EmailStr = Field(..., description="Email del usuario")
    contrasena: str = Field(..., min_length=1, description="Contraseña del usuario")

@usuarios_router.post(
    "/obtener-id-persona",
    response_model=IdPersonaResponse,
    summary="Obtener id_persona por credenciales",
    description="Dado el email y contraseña del usuario, retorna el id_persona asociado."
)
async def obtener_id_persona_por_credenciales_endpoint(
    credenciales: CredencialesRequest = Body(...)
):
    try:
        id_persona = obtener_id_persona_por_credenciales(
            email=credenciales.email,
            contrasena=credenciales.contrasena
        )
        if id_persona is None:
            # Si retorna None, puede ser porque las credenciales son incorrectas
            # o porque el usuario no tiene id_persona asignado
            # Por seguridad, no revelamos cuál es el caso
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o usuario sin persona asignada"
            )
        return IdPersonaResponse(id_persona=id_persona)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class AsignarPersonaRequest(BaseModel):
    """Modelo de request para asignar un usuario a una persona."""
    id_persona: int = Field(..., gt=0, description="ID de la persona a asignar")
    tipoUsuario: TipoUsuario = Field(..., description="Tipo de usuario")

@usuarios_router.put(
    "/{id_usuario}/asignar-persona",
    response_model=Usuario,
    summary="Asignar usuario a persona",
    description="Asigna un usuario a una persona actualizando id_persona y tipoUsuario."
)
async def asignar_usuario_a_persona(
    id_usuario: int = Path(..., gt=0, description="ID del usuario"),
    request: AsignarPersonaRequest = Body(...)
):
    try:
        actualizado = actualizarUsuarioPersona(
            id_usuario=id_usuario,
            id_persona=request.id_persona,
            tipo_usuario=request.tipoUsuario
        )
        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return actualizado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))