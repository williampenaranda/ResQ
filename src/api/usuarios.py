from fastapi import APIRouter, HTTPException, status
from src.security.entities.Usuario import Usuario
from src.dataLayer.dataAccesComponets.repositorioUsuarios import crearUsuario

usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@usuarios_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario y retorna un mensaje de confirmación."
)
async def crear_usuario(usuario: Usuario):
    try:
        nuevo_usuario = crearUsuario(usuario)
        if not nuevo_usuario:
            # Conflicto: usuario/email duplicado
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuario o email ya existente"
            )
        return {"mensaje": "Usuario creado correctamente"}
    except ValueError as ve:
        # Datos inválidos
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Error interno
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))