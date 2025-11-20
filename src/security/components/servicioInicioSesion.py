"""
Módulo de servicio para la gestión de inicio de sesión.
Proporciona funcionalidad para autenticar usuarios y generar tokens de acceso.
"""

from typing import Optional, Dict
from fastapi import HTTPException, status
from src.dataLayer.dataAccesComponets.repositorioUsuarios import obtenerUsuario
from src.security.components.servicioHash import evaluarContrasena
from src.security.components.servicioAutenticacion import generar_token, verificar_token, ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel, EmailStr, Field


class LoginData(BaseModel):
    """
    Modelo para los datos de inicio de sesión.
    
    Se puede iniciar sesión con nombre de usuario o email.
    """
    username: Optional[str] = Field(None, description="Nombre de usuario")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario123",
                "password": "contraseña123"
            }
        }


class TokenResponse(BaseModel):
    """Modelo para la respuesta de login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


async def login(datos_login: LoginData) -> TokenResponse:
    """
    Autentica un usuario y genera un token de acceso.
    
    Args:
        datos_login (LoginData): Datos de inicio de sesión (usuario/email y contraseña)
        
    Returns:
        TokenResponse: Token de acceso y metadatos si la autenticación es exitosa
        
    Raises:
        HTTPException: Si las credenciales son inválidas o hay error en la autenticación
    """
    try:
        # Validar que se proporcione al menos username o email
        if not datos_login.username and not datos_login.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar nombre de usuario o email"
            )

        # Determinar el identificador (username o email)
        identificador = datos_login.username or datos_login.email
        
        # Buscar usuario
        usuario = obtenerUsuario(
            nombreDeUsuario=datos_login.username if datos_login.username else None,
            email=datos_login.email if datos_login.email else None
        )
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Verificar contraseña
        if not evaluarContrasena(datos_login.password, usuario.contrasenaHasheada):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Preparar datos del usuario para el token
        usuario_data = {
            "id": usuario.id,
            "nombreDeUsuario": usuario.nombreDeUsuario,
            "email": usuario.email,
            "tipoUsuario": usuario.tipoUsuario.value if usuario.tipoUsuario else None
        }
        
        # Generar token
        token = generar_token(usuario_data)
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el inicio de sesión: {str(e)}"
        )


async def verify_current_user(token: str) -> Dict:
    """
    Verifica el token del usuario actual y retorna sus datos.
    
    Args:
        token (str): Token JWT a verificar
        
    Returns:
        dict: Datos del usuario contenidos en el token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = verificar_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        username = payload.get("sub") or payload.get("nombreDeUsuario")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )