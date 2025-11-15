"""
Módulo de servicios para la gestión de usuarios.
Proporciona funciones para crear, actualizar y gestionar usuarios en el sistema.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.security.entities.Usuario import Usuario, TipoUsuario
from src.security.components.servicioHash import hasearContrasena, evaluarContrasena
from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloUsuario import Usuario as UsuarioDB


def _mapear_db_a_be(usuario_db: UsuarioDB) -> Usuario:
    """Helper para mapear de modelo de BD a entidad de negocio."""
    tipo_usuario = None
    if usuario_db.tipoUsuario:
        try:
            tipo_usuario = TipoUsuario(usuario_db.tipoUsuario)
        except ValueError:
            tipo_usuario = None
    
    return Usuario(
        id=usuario_db.id,
        nombreDeUsuario=usuario_db.nombreDeUsuario,
        email=usuario_db.email,
        contrasenaHasheada=usuario_db.contrasenaHasheada,
        id_persona=usuario_db.id_persona,
        tipoUsuario=tipo_usuario
    )


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
        usuario_db = UsuarioDB(
            nombreDeUsuario=usuario.nombreDeUsuario,
            email=usuario.email,
            contrasenaHasheada=hasearContrasena(usuario.contrasenaHasheada),
            id_persona=None,  # Por defecto null al crear
            tipoUsuario=None  # Por defecto null al crear
        )
        
        # Obtener sesión y guardar
        sesion = SessionLocal()
        try:
            sesion.add(usuario_db)
            sesion.commit()
            sesion.refresh(usuario_db)  # Refrescar para obtener el ID generado
            
            # Crear y retornar el modelo Pydantic con los datos guardados
            usuario_creado = Usuario(
                id=usuario_db.id,
                nombreDeUsuario=usuario_db.nombreDeUsuario,
                email=usuario_db.email,
                contrasenaHasheada=usuario_db.contrasenaHasheada,
                id_persona=usuario_db.id_persona,
                tipoUsuario=None  # Retornar null como se pidió
            )
            return usuario_creado
            
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

    sesion = SessionLocal()
    try:
        # Construir el filtro de búsqueda
        query = sesion.query(UsuarioDB)
        
        if nombreDeUsuario:
            query = query.filter(UsuarioDB.nombreDeUsuario == nombreDeUsuario)
        if email:
            query = query.filter(UsuarioDB.email == email)
            
        # Realizar la búsqueda
        usuario_db = query.first()
        
        # Convertir el resultado a modelo Pydantic si existe
        return _mapear_db_a_be(usuario_db) if usuario_db else None
        
    except Exception as e:
        # Log del error aquí si tienes sistema de logging
        raise RuntimeError(f"Error al buscar usuario: {str(e)}")
        
    finally:
        sesion.close()


def obtener_usuario_por_id(id_usuario: int) -> Optional[Usuario]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        id_usuario (int): ID del usuario a buscar
        
    Returns:
        Optional[Usuario]: Usuario encontrado o None si no existe
        
    Raises:
        ValueError: Si el ID es inválido
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("id_usuario debe ser un entero positivo")
    
    sesion = SessionLocal()
    try:
        usuario_db = sesion.query(UsuarioDB).filter(UsuarioDB.id == id_usuario).first()
        return _mapear_db_a_be(usuario_db) if usuario_db else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener usuario por id: {e}")
    finally:
        sesion.close()


def listar_usuarios(limit: int = 50, offset: int = 0) -> List[Usuario]:
    """
    Lista usuarios con paginación.
    
    Args:
        limit (int): Cantidad máxima de registros (default: 50)
        offset (int): Desplazamiento para paginación (default: 0)
        
    Returns:
        List[Usuario]: Lista de usuarios
        
    Raises:
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    sesion = SessionLocal()
    try:
        query = sesion.query(UsuarioDB).order_by(UsuarioDB.id).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar usuarios: {e}")
    finally:
        sesion.close()


def actualizar_usuario(id_usuario: int, cambios: Dict[str, Any]) -> Optional[Usuario]:
    """
    Actualiza campos de un usuario.
    
    Args:
        id_usuario (int): ID del usuario a actualizar
        cambios (Dict[str, Any]): Diccionario con los campos a actualizar
        
    Returns:
        Optional[Usuario]: Usuario actualizado o None si no existe
        
    Raises:
        ValueError: Si los datos son inválidos
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("id_usuario debe ser un entero positivo")
    if not isinstance(cambios, dict) or not cambios:
        raise ValueError("Debe proporcionar un diccionario de cambios")
    
    sesion = SessionLocal()
    try:
        usuario_db = sesion.query(UsuarioDB).filter(UsuarioDB.id == id_usuario).first()
        if not usuario_db:
            return None
        
        # Actualizar campos permitidos
        if "nombreDeUsuario" in cambios:
            usuario_db.nombreDeUsuario = cambios["nombreDeUsuario"].strip() if isinstance(cambios["nombreDeUsuario"], str) else cambios["nombreDeUsuario"]
        if "email" in cambios:
            usuario_db.email = cambios["email"]
        if "contrasenaHasheada" in cambios:
            # Hashear la contraseña si se proporciona
            usuario_db.contrasenaHasheada = hasearContrasena(cambios["contrasenaHasheada"])
        if "id_persona" in cambios:
            usuario_db.id_persona = cambios["id_persona"]
        if "tipoUsuario" in cambios:
            if isinstance(cambios["tipoUsuario"], TipoUsuario):
                usuario_db.tipoUsuario = cambios["tipoUsuario"].value
            elif isinstance(cambios["tipoUsuario"], str):
                usuario_db.tipoUsuario = cambios["tipoUsuario"]
            else:
                usuario_db.tipoUsuario = None
        
        sesion.commit()
        sesion.refresh(usuario_db)
        return _mapear_db_a_be(usuario_db)
    except IntegrityError:
        sesion.rollback()
        return None  # Conflicto de unicidad
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al actualizar usuario: {e}")
    finally:
        sesion.close()


def eliminar_usuario(id_usuario: int) -> bool:
    """
    Elimina un usuario por su ID.
    
    Args:
        id_usuario (int): ID del usuario a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False si no existe
        
    Raises:
        ValueError: Si el ID es inválido
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("id_usuario debe ser un entero positivo")
    
    sesion = SessionLocal()
    try:
        usuario_db = sesion.query(UsuarioDB).filter(UsuarioDB.id == id_usuario).first()
        if not usuario_db:
            return False
        sesion.delete(usuario_db)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar usuario: {e}")
    finally:
        sesion.close()


def obtener_id_persona_por_credenciales(email: str, contrasena: str) -> Optional[int]:
    """
    Obtiene el id_persona de un usuario validando su email y contraseña.
    
    Args:
        email (str): Email del usuario
        contrasena (str): Contraseña en texto plano
        
    Returns:
        Optional[int]: id_persona si las credenciales son correctas, None si no
        
    Raises:
        ValueError: Si los datos son inválidos
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not email or not isinstance(email, str) or not email.strip():
        raise ValueError("El email es requerido")
    if not contrasena or not isinstance(contrasena, str) or not contrasena.strip():
        raise ValueError("La contraseña es requerida")
    
    sesion = SessionLocal()
    try:
        usuario_db = sesion.query(UsuarioDB).filter(UsuarioDB.email == email.strip()).first()
        if not usuario_db:
            return None
        
        # Verificar la contraseña
        if not evaluarContrasena(contrasena, usuario_db.contrasenaHasheada):
            return None
        
        # Retornar el id_persona (puede ser None si no está asignado)
        return usuario_db.id_persona
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener id_persona por credenciales: {e}")
    finally:
        sesion.close()


def actualizarUsuarioPersona(id_usuario: int, id_persona: int, tipo_usuario: TipoUsuario) -> Optional[Usuario]:
    """
    Asigna un usuario a una persona actualizando id_persona y tipoUsuario.
    
    Args:
        id_usuario (int): ID del usuario a actualizar
        id_persona (int): ID de la persona a asignar
        tipo_usuario (TipoUsuario): Tipo de usuario a asignar
        
    Returns:
        Optional[Usuario]: Usuario actualizado o None si no existe
        
    Raises:
        ValueError: Si los datos son inválidos
        RuntimeError: Si hay un error en la conexión con la base de datos
    """
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("id_usuario debe ser un entero positivo")
    if not isinstance(id_persona, int) or id_persona <= 0:
        raise ValueError("id_persona debe ser un entero positivo")
    if not isinstance(tipo_usuario, TipoUsuario):
        raise ValueError("tipo_usuario debe ser una instancia de TipoUsuario")
    
    return actualizar_usuario(id_usuario, {
        "id_persona": id_persona,
        "tipoUsuario": tipo_usuario
    })

