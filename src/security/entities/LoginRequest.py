"""
Modelos Pydantic para las requests de autenticación.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Modelo para la request de login."""
    
    identificador: str = Field(
        ...,
        description="Email o nombre de usuario",
        min_length=1
    )
    contrasena: str = Field(
        ...,
        description="Contraseña del usuario",
        min_length=1
    )


class TokenRequest(BaseModel):
    """Modelo para la request de verificación de token."""
    
    token: str = Field(
        ...,
        description="Token JWT a verificar",
        min_length=1
    )


class TokenResponse(BaseModel):
    """Modelo para la response de login."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenVerifyResponse(BaseModel):
    """Modelo para la response de verificación de token."""
    
    valid: bool
    usuario: dict | None = None
    mensaje: str | None = None

