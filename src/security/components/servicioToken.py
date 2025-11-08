"""
Módulo de servicio para la gestión de tokens JWT.
Proporciona funcionalidad para crear y verificar tokens de acceso JWT.
"""

from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os

# Cargar variables de entorno
load_dotenv()

# Constantes
DEFAULT_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

# Validar configuración crítica
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está configurada en las variables de entorno")

class Token(BaseModel):
    """
    Modelo Pydantic para la respuesta de token.
    
    Attributes:
        accessToken (str): Token JWT generado
        tokenType (str): Tipo de token (Bearer por defecto)
    """
    accessToken: str = Field(..., description="Token JWT de acceso")
    tokenType: str = Field(default="Bearer", description="Tipo de token")

    class Config:
        json_schema_extra = {
            "example": {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                "tokenType": "Bearer"
            }
        }

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data (Dict[str, Any]): Datos a codificar en el token
        expires_delta (Optional[timedelta]): Tiempo de expiración personalizado
            
    Returns:
        str: Token JWT codificado
        
    Raises:
        ValueError: Si los datos están vacíos
        RuntimeError: Si hay un error al codificar el token
    """
    if not data:
        raise ValueError("Los datos del token no pueden estar vacíos")
        
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta
            else timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)
        )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc)  # Tiempo de emisión
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
    except Exception as e:
        raise RuntimeError(f"Error al crear el token: {str(e)}")

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token (str): Token JWT a verificar
            
    Returns:
        Dict[str, Any]: Datos decodificados del token
        
    Raises:
        InvalidTokenError: Si el token es inválido
        ExpiredSignatureError: Si el token ha expirado
        RuntimeError: Si hay otro error al decodificar
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
        
    except ExpiredSignatureError:
        raise ExpiredSignatureError("El token ha expirado")
        
    except InvalidTokenError as e:
        raise InvalidTokenError(f"Token inválido: {str(e)}")
        
    except Exception as e:
        raise RuntimeError(f"Error al verificar el token: {str(e)}")

def create_token_response(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> Token:
    """
    Crea una respuesta de token completa con el token y su tipo.
    
    Args:
        data (Dict[str, Any]): Datos a codificar en el token
        expires_delta (Optional[timedelta]): Tiempo de expiración personalizado
            
    Returns:
        Token: Modelo Token con el token JWT y su tipo
    """
    access_token = create_access_token(data, expires_delta)
    return Token(accessToken=access_token)
