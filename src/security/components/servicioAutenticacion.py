"""
Módulo de servicios de autenticación con JWT.

Este módulo proporciona funciones para:
1. Generar tokens JWT
2. Verificar tokens JWT
3. Autenticar usuarios con credenciales
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import jwt
from src.security.components.servicioUsuarios import obtenerUsuario
from src.security.components.servicioHash import evaluarContrasena

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 horas por defecto


def generar_token(usuario_data: Dict) -> str:
    """
    Genera un token JWT para un usuario.
    
    Args:
        usuario_data (Dict): Diccionario con datos del usuario (nombreDeUsuario, email, etc.)
        
    Returns:
        str: Token JWT codificado
    """
    # Calcular tiempo de expiración
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload del token
    payload = {
        "sub": usuario_data.get("email") or usuario_data.get("nombreDeUsuario"),  # Subject (identificador)
        "nombreDeUsuario": usuario_data.get("nombreDeUsuario"),
        "email": usuario_data.get("email"),
        "exp": expire,  # Expiración
        "iat": datetime.now(timezone.utc),  # Issued at (emitido en)
    }
    
    # Generar token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_token(token: str) -> Optional[Dict]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token (str): Token JWT a verificar
        
    Returns:
        Optional[Dict]: Payload del token si es válido, None si es inválido o expirado
        
    Raises:
        jwt.ExpiredSignatureError: Si el token ha expirado
        jwt.InvalidTokenError: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


def autenticar_usuario(identificador: str, contrasena: str) -> Optional[Dict]:
    """
    Autentica un usuario con su email/nombreDeUsuario y contraseña.
    
    Args:
        identificador (str): Email o nombre de usuario
        contrasena (str): Contraseña en texto plano
        
    Returns:
        Optional[Dict]: Diccionario con datos del usuario si la autenticación es exitosa,
            None si las credenciales son incorrectas
    """
    # Intentar buscar por email primero, luego por nombreDeUsuario
    usuario = obtenerUsuario(email=identificador)
    if not usuario:
        usuario = obtenerUsuario(nombreDeUsuario=identificador)
    
    # Si no se encontró el usuario, retornar None
    if not usuario:
        return None
    
    # Verificar la contraseña
    if not evaluarContrasena(contrasena, usuario.contrasenaHasheada):
        return None
    
    # Retornar datos del usuario (sin la contraseña)
    return {
        "nombreDeUsuario": usuario.nombreDeUsuario,
        "email": usuario.email,
    }

