from pydantic import BaseModel, EmailStr, Field, field_validator
import enum
from typing import Optional

class TipoUsuario(enum.Enum):
    OPERADOR_AMBULANCIA = "OPERADOR_AMBULANCIA"
    OPERADOR_EMERGENCIA = "OPERADOR_EMERGENCIA"
    SOLICITANTE = "SOLICITANTE"
    ADMINISTRADOR = "ADMINISTRADOR"

class Usuario(BaseModel):
    """Modelo Pydantic (v2) que representa un usuario.

    Campos:
    - nombreDeUsuario: nombre de usuario (cadena no vacía)
    - email: email (validado con EmailStr)
    - contrasenaHasheada: contraseña ya hasheada (cadena no vacía)
    """
    id: Optional[int] = None
    id_persona: Optional[int] = None
    nombreDeUsuario: str = Field(..., min_length=1)
    email: EmailStr
    contrasenaHasheada: str = Field(..., min_length=1)
    tipoUsuario: TipoUsuario
    

    # Normalizar/validar campos simples
    @field_validator("nombreDeUsuario", mode="before")
    def _strip_nombre(cls, v):
        if v is None:
            raise ValueError("nombreDeUsuario es requerido")
        if not isinstance(v, str):
            raise TypeError("nombreDeUsuario debe ser una cadena")
        v = v.strip()
        if not v:
            raise ValueError("nombreDeUsuario no puede estar vacío")
        return v

    @field_validator("contrasenaHasheada", mode="before")
    def _validate_contrasena(cls, v):
        if v is None:
            raise ValueError("contrasenaHasheada es requerida")
        if not isinstance(v, str):
            raise TypeError("contrasenaHasheada debe ser una cadena")
        if not v:
            raise ValueError("contrasenaHasheada no puede estar vacía")
        return v

    class Config:
        # Por seguridad, prohibir campos extra inesperados
        extra = "forbid"

