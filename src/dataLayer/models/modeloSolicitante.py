"""
Modelo de base de datos para la tabla de solicitantes.

Define la estructura de la tabla 'solicitantes' utilizando SQLAlchemy ORM.
Los campos se alinean con la entidad Pydantic `Solicitante` (que hereda de `Persona`)
e incluyen `padecimientos` almacenado como JSON para simplicidad.
"""

from datetime import date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.types import JSON
from sqlalchemy import Enum as SAEnum

# Reutilizamos la misma Base y helper de timestamps que el modelo de Usuario
from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento


class Solicitante(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'solicitantes'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - nombre, nombre2: Nombres (nombre2 opcional)
    - apellido, apellido2: Apellidos (apellido2 opcional)
    - fechaNacimiento: Fecha de nacimiento
    - documento: Tipo genérico de documento (texto)
    - tipoDocumento: Tipo de documento (CC, CE, etc.) almacenado como texto
    - numeroDocumento: Número del documento
    - padecimientos: Lista de padecimientos (JSON)
    - fechaCreacion / fechaActualizacion: Timestamps en UTC

    Restricciones:
    - Unicidad compuesta en (tipoDocumento, numeroDocumento)
    """

    __tablename__ = "solicitantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Datos personales
    nombre = Column(String(100), nullable=False)
    nombre2 = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=False)
    apellido2 = Column(String(100), nullable=True)
    fechaNacimiento = Column(Date, nullable=False)

    # Documento de identidad
    documento = Column(String(50), nullable=False)  # Campo libre si se usa
    tipoDocumento = Column(SAEnum(TipoDocumento, name="tipo_documento_enum"), nullable=False, index=True)
    numeroDocumento = Column(String(100), nullable=False, index=True)

    # Información médica
    padecimientos = Column(JSON, nullable=False, default=list)

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(
        DateTime(timezone=True),
        default=obtener_fecha_utc,
        onupdate=obtener_fecha_utc,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("tipoDocumento", "numeroDocumento", name="uq_solicitante_documento"),
    )

    def __repr__(self):
        return (
            f"<Solicitante(id={self.id}, nombre='{self.nombre}', apellido='{self.apellido}', "
            f"tipoDocumento='{self.tipoDocumento}', numeroDocumento='{self.numeroDocumento}')>"
        )

    def __str__(self):
        return (
            f"Solicitante(id={self.id}, nombre='{self.nombre}', apellido='{self.apellido}', "
            f"tipoDocumento='{self.tipoDocumento}', numeroDocumento='{self.numeroDocumento}')"
        )

