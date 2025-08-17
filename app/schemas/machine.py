from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.machine import StopReason


class MachineBase(BaseModel):
    name: str
    location: Optional[str] = None


class MachineCreate(MachineBase):
    pass


class MachineOut(MachineBase):
    id: int

    class Config:
        from_attributes = True


class ProductionEventBase(BaseModel):
    machine_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    stop_reason: Optional[StopReason] = None
    quantity: int = 0


class ProductionEventCreate(ProductionEventBase):
    pass


class ProductionEventOut(ProductionEventBase):
    id: int

    class Config:
        from_attributes = True
