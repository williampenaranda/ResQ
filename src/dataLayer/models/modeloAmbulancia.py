"""
Modelo de base de datos para la tabla de ambulancias.

Define la estructura de la tabla 'ambulancias' utilizando SQLAlchemy ORM.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy import Enum as SAEnum

from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia


class Ambulancia(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'ambulancias'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - disponibilidad: Disponibilidad de la ambulancia (booleano)
    - placa: Placa de la ambulancia
    - tipoAmbulancia: Tipo de ambulancia (Enum)
    - ubicacion_id: ID de la ubicación (FK a ubicaciones.id)
    - fechaCreacion / fechaActualizacion: Timestamps en UTC
    """

    __tablename__ = "ambulancias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Datos de la ambulancia
    disponibilidad = Column(Boolean, nullable=False, default=False)
    placa = Column(String(20), nullable=False, unique=True, index=True)
    tipoAmbulancia = Column(
        SAEnum(TipoAmbulancia, name="tipo_ambulancia_enum"),
        nullable=False
    )

    # Relación con ubicación
    ubicacion_id = Column(
        Integer,
        ForeignKey("ubicaciones.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    # Relación con operador de ambulancia
    id_operador_ambulancia = Column(
        Integer,
        ForeignKey("operadores_ambulancia.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(
        DateTime(timezone=True),
        default=obtener_fecha_utc,
        onupdate=obtener_fecha_utc,
        nullable=False,
    )

    def __repr__(self):
        return f"<Ambulancia(id={self.id}, placa='{self.placa}', tipoAmbulancia={self.tipoAmbulancia}, disponibilidad={self.disponibilidad})>"

    def __str__(self):
        return f"Ambulancia(id={self.id}, placa='{self.placa}', tipoAmbulancia={self.tipoAmbulancia.value}, disponibilidad={self.disponibilidad})"

