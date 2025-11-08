"""
Módulo de servicio para la gestión de inicio de sesión.
Proporciona funcionalidad para autenticar usuarios y generar tokens de acceso.
"""

from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status
from src.security.components.servicioUsuarios import obtenerUsuario
from src.security.components.servicioHash import evaluarContrasena
from src.security.components.servicioToken import Token, create_token_response
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

async def login(datos_login: LoginData) -> Token:
    """
    Autentica un usuario y genera un token de acceso.
    
    Args:
        datos_login (LoginData): Datos de inicio de sesión (usuario/email y contraseña)
        
    Returns:
        Token: Token de acceso si la autenticación es exitosa
        
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

        # Buscar usuario
        usuario = obtenerUsuario(
            nombreDeUsuario=datos_login.username,
            email=datos_login.email
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
            
        # Generar token
        token_data = {
            "sub": usuario.nombreDeUsuario,
            "email": usuario.email
        }
        
        # Por defecto el token expira en 15 minutos (configurado en servicioToken)
        return create_token_response(token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el inicio de sesión: {str(e)}"
        )

async def verify_current_user(token: str) -> dict:
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
        from src.security.components.servicioToken import verify_token
        
        payload = verify_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )