"""
Módulo de servicios para la gestión de usuarios.
Proporciona funciones para crear, actualizar y gestionar usuarios en el sistema.
"""

from typing import Optional
from sqlalchemy.exc import IntegrityError
from src.security.entities.Usuario import Usuario
from src.security.components.servicioHash import hasearContrasena
from src.dataLayer.bd import obtener_sesion
from src.dataLayer.models import modeloUsuario

def crearUsuario(usuario: Usuario) -> Optional[Usuario]:
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        usuario (Usuario): Instancia de Usuario con los datos del nuevo usuario.
            Debe incluir nombreDeUsuario, email y contraseña sin hashear.
            
    Returns:
        Optional[Usuario]: El usuario creado si fue exitoso, None si hubo un error
            de integridad (e.g., usuario o email duplicado)
            
    Raises:
        ValueError: Si los datos del usuario son inválidos
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    try:
        # Validar que el usuario sea una instancia de Usuario
        if not isinstance(usuario, Usuario):
            raise ValueError("El parámetro debe ser una instancia de Usuario")
            
        # Crear modelo de BD a partir del Pydantic model
        usuario_db = modeloUsuario(
            nombreDeUsuario=usuario.nombreDeUsuario,
            email=usuario.email,
            contrasenaHasheada=hasearContrasena(usuario.contrasenaHasheada)
        )
        
        # Obtener sesión y guardar
        sesion = obtener_sesion()
        try:
            sesion.add(usuario_db)
            sesion.commit()
            
            # Actualizar el modelo Pydantic con los datos guardados
            usuario.contrasenaHasheada = usuario_db.contrasenaHasheada
            return usuario
            
        except IntegrityError:
            sesion.rollback()
            return None  # Usuario duplicado
            
        finally:
            sesion.close()
            
    except Exception as e:
        # Log del error aquí si tienes sistema de logging
        raise RuntimeError(f"Error al crear usuario: {str(e)}")

def obtenerUsuario(nombreDeUsuario: str = None, email: str = None) -> Optional[Usuario]:
    """
    Busca y retorna un usuario por su nombre de usuario o email.
    
    Args:
        nombreDeUsuario (str, optional): Nombre de usuario a buscar
        email (str, optional): Email del usuario a buscar
        
    Returns:
        Optional[Usuario]: Usuario encontrado o None si no existe
        
    Raises:
        ValueError: Si no se proporciona ningún criterio de búsqueda
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not nombreDeUsuario and not email:
        raise ValueError("Debe proporcionar nombreDeUsuario o email para la búsqueda")

    sesion = obtener_sesion()
    try:
        # Construir el filtro de búsqueda
        filtro = []
        if nombreDeUsuario:
            filtro.append(modeloUsuario.nombreDeUsuario == nombreDeUsuario)
        if email:
            filtro.append(modeloUsuario.email == email)
            
        # Realizar la búsqueda
        usuario_db = sesion.query(modeloUsuario).filter(*filtro).first()
        
        # Convertir el resultado a modelo Pydantic si existe
        if usuario_db:
            return Usuario(
                nombreDeUsuario=usuario_db.nombreDeUsuario,
                email=usuario_db.email,
                contrasenaHasheada=usuario_db.contrasenaHasheada
            )
        return None
        
    except Exception as e:
        # Log del error aquí si tienes sistema de logging
        raise RuntimeError(f"Error al buscar usuario: {str(e)}")
        
    finally:
        sesion.close()

