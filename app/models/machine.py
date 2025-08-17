from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum


class StopReason(str, enum.Enum):
    falta_material = "falta_material"
    manutencao = "manutencao"
    falha_eletrica = "falha_eletrica"
    setup = "setup"
    qualidade = "qualidade"


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    location = Column(String(120), nullable=True)

    events = relationship("ProductionEvent", back_populates="machine")


class ProductionEvent(Base):
    __tablename__ = "production_events"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=False)  # operating | stopped
    stop_reason = Column(Enum(StopReason), nullable=True)
    quantity = Column(Integer, default=0, nullable=False)  # produzida no período

    machine = relationship("Machine", back_populates="events")
