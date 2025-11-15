"""
Modelo de base de datos para la tabla de solicitudes.

Define la estructura de la tabla 'solicitudes' utilizando SQLAlchemy ORM.
Relaciona con Solicitante y Ubicacion mediante claves foráneas.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

# Reutilizamos la misma Base y helper de timestamps que el modelo de Usuario
from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc


class Solicitud(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'solicitudes'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - solicitante_id: ID del solicitante (FK a solicitantes.id)
    - ubicacion_id: ID de la ubicación (FK a ubicaciones.id)
    - fechaHora: Fecha y hora de la solicitud
    - fechaCreacion / fechaActualizacion: Timestamps en UTC
    """

    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Relaciones
    solicitante_id = Column(
        Integer,
        ForeignKey("solicitantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ubicacion_id = Column(
        Integer,
        ForeignKey("ubicaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Fecha y hora de la solicitud
    fechaHora = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(
        DateTime(timezone=True),
        default=obtener_fecha_utc,
        onupdate=obtener_fecha_utc,
        nullable=False,
    )

    def __repr__(self):
        return f"<Solicitud(id={self.id}, solicitante_id={self.solicitante_id}, ubicacion_id={self.ubicacion_id}, fechaHora={self.fechaHora})>"

    def __str__(self):
        return f"Solicitud(id={self.id}, solicitante_id={self.solicitante_id}, ubicacion_id={self.ubicacion_id}, fechaHora={self.fechaHora})"
