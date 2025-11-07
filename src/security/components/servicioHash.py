"""
Módulo de servicios de hash para contraseñas utilizando bcrypt.

Este módulo proporciona funciones para:
1. Generar hashes seguros de contraseñas
2. Verificar contraseñas contra hashes existentes

Utiliza bcrypt como algoritmo de hash, que:
- Incorpora automáticamente un salt único por contraseña
- Implementa un factor de trabajo adaptativo
- Es resistente a ataques por hardware especializado
"""

import bcrypt

# Generamos un salt global para el proceso de hashing
# Nota: bcrypt.gensalt() genera un salt criptográficamente seguro


def hasearContrasena(contrasena: str) -> str:
    """
    Genera un hash seguro para una contraseña usando bcrypt.
    
    Args:
        contrasena (str): La contraseña en texto plano a hashear
        
    Returns:
        str: El hash de la contraseña (60 caracteres)
        
    Raises:
        TypeError: Si la contraseña no es una cadena
        ValueError: Si la contraseña está vacía
    """
    if not isinstance(contrasena, str):
        raise TypeError("La contraseña debe ser una cadena")
    if not contrasena:
        raise ValueError("La contraseña no puede estar vacía")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), salt) # Hash de la contraseña
    return hashed_password.decode('utf-8') # Devolvemos el hash como una cadena de texto

def evaluarContrasena(contrasena: str, hash: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        contrasena (str): La contraseña en texto plano a verificar
        hash (str): El hash contra el cual verificar la contraseña
        
    Returns:
        bool: True si la contraseña coincide con el hash, False en caso contrario
        
    Raises:
        TypeError: Si la contraseña o el hash no son cadenas
        ValueError: Si la contraseña o el hash están vacíos
    """
    if not isinstance(contrasena, str) or not isinstance(hash, str):
        raise TypeError("La contraseña y el hash deben ser cadenas")
    if not contrasena or not hash:
        raise ValueError("La contraseña y el hash no pueden estar vacíos")
        
    return bcrypt.checkpw(contrasena.encode('utf-8'), hash.encode('utf-8'))
