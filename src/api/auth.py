"""
Endpoints de autenticación.

Este módulo proporciona endpoints para:
1. Login con credenciales (email/nombreDeUsuario + contraseña)
2. Verificación de token JWT
"""

from fastapi import APIRouter, HTTPException, status
from src.security.entities.LoginRequest import (
    LoginRequest,
    TokenRequest,
    TokenResponse,
    TokenVerifyResponse
)
from src.security.components.servicioAutenticacion import (
    autenticar_usuario,
    generar_token,
    verificar_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["autenticación"]
)


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """
    Endpoint para autenticar un usuario y obtener un token JWT.
    
    Acepta email o nombreDeUsuario junto con la contraseña.
    
    Returns:
        TokenResponse: Token JWT y metadatos
    """
    # Autenticar usuario
    usuario = autenticar_usuario(
        login_request.identificador,
        login_request.contrasena
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Generar token
    token = generar_token(usuario)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
    )


@auth_router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(token_request: TokenRequest):
    """
    Endpoint para verificar si un token JWT es válido.
    
    Returns:
        TokenVerifyResponse: Información sobre la validez del token
    """
    # Verificar token
    payload = verificar_token(token_request.token)
    
    if not payload:
        return TokenVerifyResponse(
            valid=False,
            mensaje="Token inválido o expirado"
        )
    
    # Extraer información del usuario del payload
    usuario_info = {
        "nombreDeUsuario": payload.get("nombreDeUsuario"),
        "email": payload.get("email"),
        "sub": payload.get("sub")
    }
    
    return TokenVerifyResponse(
        valid=True,
        usuario=usuario_info,
        mensaje="Token válido"
    )

