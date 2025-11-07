"""
Modelo de base de datos para la tabla de usuarios.

Este módulo define la estructura de la tabla 'usuarios' en la base de datos
utilizando SQLAlchemy ORM.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def obtener_fecha_utc():
    """
    Función helper para obtener la fecha y hora actual en UTC.
    Usa datetime.now(timezone.utc) en lugar de datetime.utcnow() que está deprecado.
    """
    return datetime.now(timezone.utc)


class ModeloUsuario(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'usuarios' en la base de datos.
    
    Campos:
    - id: Identificador único del usuario (clave primaria, autoincremental)
    - nombreDeUsuario: Nombre de usuario (único, no nulo)
    - email: Email del usuario (único, no nulo)
    - contrasenaHasheada: Contraseña hasheada con bcrypt (no nulo)
    - fechaCreacion: Fecha y hora de creación del registro
    - fechaActualizacion: Fecha y hora de última actualización
    """
    
    __tablename__ = "usuarios"
    
    # Clave primaria
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Campos del usuario
    nombreDeUsuario = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    contrasenaHasheada = Column(String(60), nullable=False)  # bcrypt genera hashes de 60 caracteres
    
    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, onupdate=obtener_fecha_utc, nullable=False)
    
    # Constraint adicional para asegurar unicidad
    __table_args__ = (
        UniqueConstraint('nombreDeUsuario', name='uq_nombre_usuario'),
        UniqueConstraint('email', name='uq_email'),
    )
    
    def __repr__(self):
        return f"<ModeloUsuario(id={self.id}, nombreDeUsuario='{self.nombreDeUsuario}', email='{self.email}')>"
