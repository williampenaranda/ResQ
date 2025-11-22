"""
Modelo de base de datos para la tabla de órdenes de despacho.

Define la estructura de la tabla 'ordenes_despacho' utilizando SQLAlchemy ORM.
Relaciona con Emergencia, Ambulancia, OperadorAmbulancia y OperadorEmergencia.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from src.dataLayer.models.modeloUsuario import Base, obtener_fecha_utc


class OrdenDespacho(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'ordenes_despacho'.

    Campos:
    - id: Identificador único (PK, autoincremental)
    - fechaHora: Fecha y hora de la orden de despacho
    - emergencia_id: ID de la emergencia (FK a emergencias.id)
    - ambulancia_id: ID de la ambulancia (FK a ambulancias.id)
    - operador_ambulancia_id: ID del operador de ambulancia (FK a operadores_ambulancia.id)
    - operador_emergencia_id: ID del operador de emergencia (FK a operadores_emergencia.id)
    - fechaCreacion / fechaActualizacion: Timestamps en UTC
    """

    __tablename__ = "ordenes_despacho"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Relaciones
    emergencia_id = Column(
        Integer,
        ForeignKey("emergencias.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ambulancia_id = Column(
        Integer,
        ForeignKey("ambulancias.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    operador_ambulancia_id = Column(
        Integer,
        ForeignKey("operadores_ambulancia.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )
    operador_emergencia_id = Column(
        Integer,
        ForeignKey("operadores_emergencia.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )

    # Campos de la orden de despacho
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
        return f"<OrdenDespacho(id={self.id}, emergencia_id={self.emergencia_id}, ambulancia_id={self.ambulancia_id})>"

    def __str__(self):
        return f"OrdenDespacho(id={self.id}, emergencia_id={self.emergencia_id}, ambulancia_id={self.ambulancia_id}, fechaHora={self.fechaHora})"
