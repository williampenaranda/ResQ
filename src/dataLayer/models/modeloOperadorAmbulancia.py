"""
Modelo de base de datos para la tabla de operadores de ambulancia.

Define la estructura de la tabla 'operadores_ambulancia' utilizando SQLAlchemy ORM.
Los campos se alinean con la entidad Pydantic `OperadorAmbulancia` (que hereda de `Persona`)
e incluyen `disponibilidad` y `licencia` almacenados como booleano y string para simplicidad.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy import Enum as SAEnum

from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento


class OperadorAmbulancia(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'operadores_ambulancia'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - nombre, nombre2: Nombres (nombre2 opcional)
    - apellido, apellido2: Apellidos (apellido2 opcional)
    - fechaNacimiento: Fecha de nacimiento
    - tipoDocumento: Tipo de documento (Enum)
    - numeroDocumento: Número del documento
    - disponibilidad: Disponibilidad del operador (booleano)
    - licencia: Licencia del operador (string)
    - fechaCreacion / fechaActualizacion: Timestamps en UTC

    Restricciones:
    - Unicidad compuesta en (tipoDocumento, numeroDocumento)
    """

    __tablename__ = "operadores_ambulancia"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Datos personales
    nombre = Column(String(100), nullable=False)
    nombre2 = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=False)
    apellido2 = Column(String(100), nullable=True)
    fechaNacimiento = Column(Date, nullable=False)

    # Documento de identidad
    tipoDocumento = Column(SAEnum(TipoDocumento, name="tipo_documento_enum"), nullable=False, index=True)
    numeroDocumento = Column(String(100), nullable=False, index=True)

    # Datos laborales
    disponibilidad = Column(Boolean, nullable=False, default=False)
    licencia = Column(String(100), nullable=False)

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, onupdate=obtener_fecha_utc, nullable=False)

    __table_args__ = (UniqueConstraint("tipoDocumento", "numeroDocumento", name="uq_operador_ambulancia_documento"),)

