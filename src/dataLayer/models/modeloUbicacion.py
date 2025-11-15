"""
Modelo de base de datos para la tabla de ubicaciones.

Define la estructura de la tabla 'ubicaciones' utilizando SQLAlchemy ORM.
"""

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
)
from datetime import datetime, timezone

# Reutilizamos la misma Base y helper de timestamps que el modelo de Usuario
from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc


class Ubicacion(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'ubicaciones'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - latitud: Latitud GPS (-90 a 90)
    - longitud: Longitud GPS (-180 a 180)
    - fechaHora: Fecha y hora de captura de la ubicación
    - fechaCreacion / fechaActualizacion: Timestamps en UTC
    """

    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    fechaHora = Column(DateTime(timezone=True), nullable=False, default=obtener_fecha_utc)

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(
        DateTime(timezone=True),
        default=obtener_fecha_utc,
        onupdate=obtener_fecha_utc,
        nullable=False,
    )

    def __repr__(self):
        return f"<Ubicacion(id={self.id}, latitud={self.latitud}, longitud={self.longitud}, fechaHora={self.fechaHora})>"

    def __str__(self):
        return f"Ubicacion(id={self.id}, latitud={self.latitud}, longitud={self.longitud}, fechaHora={self.fechaHora})"
