"""
Modelo de base de datos para la tabla de emergencias.

Define la estructura de la tabla 'emergencias' utilizando SQLAlchemy ORM.
Relaciona con Solicitud, OperadorEmergencia y Solicitante (como paciente).
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy import Enum as SAEnum

from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad


class Emergencia(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'emergencias'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - solicitud_id: ID de la solicitud (FK a solicitudes.id)
    - estado: Estado de la emergencia (Enum)
    - tipoAmbulancia: Tipo de ambulancia requerida (Enum)
    - nivelPrioridad: Nivel de prioridad (Enum)
    - descripcion: Descripción de la emergencia
    - id_operador: ID del operador asignado (FK a operadores_emergencia.id)
    - paciente_id: ID del paciente (FK a solicitantes.id)
    - fechaCreacion / fechaActualizacion: Timestamps en UTC
    """

    __tablename__ = "emergencias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Relaciones
    solicitud_id = Column(
        Integer,
        ForeignKey("solicitudes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_operador = Column(
        Integer,
        ForeignKey("operadores_emergencia.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )
    paciente_id = Column(
        Integer,
        ForeignKey("solicitantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Campos de la emergencia
    estado = Column(
        SAEnum(EstadoEmergencia, name="estado_emergencia_enum"),
        nullable=False,
        index=True
    )
    tipoAmbulancia = Column(
        SAEnum(TipoAmbulancia, name="tipo_ambulancia_enum"),
        nullable=False
    )
    nivelPrioridad = Column(
        SAEnum(NivelPrioridad, name="nivel_prioridad_enum"),
        nullable=False,
        index=True
    )
    descripcion = Column(String(1000), nullable=False)

    # Timestamps
    fechaCreacion = Column(DateTime(timezone=True), default=obtener_fecha_utc, nullable=False)
    fechaActualizacion = Column(
        DateTime(timezone=True),
        default=obtener_fecha_utc,
        onupdate=obtener_fecha_utc,
        nullable=False,
    )

    def __repr__(self):
        return f"<Emergencia(id={self.id}, estado={self.estado}, solicitud_id={self.solicitud_id}, paciente_id={self.paciente_id})>"

    def __str__(self):
        return f"Emergencia(id={self.id}, estado={self.estado.value}, solicitud_id={self.solicitud_id}, paciente_id={self.paciente_id})"

