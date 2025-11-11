from fastapi import APIRouter
from src.security.entities.Usuario import Usuario
from src.dataLayer.dataAccesComponets.repositorioUsuarios import crearUsuario
usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@usuarios_router.post("/")
async def crear_usuario(usuario: Usuario):
    nuevo_usuario = crearUsuario(usuario)
    if nuevo_usuario:
        return {"mensaje": "Usuario creado correctamente"}
    else:
        return {"mensaje": "Error al crear el usuario"}

