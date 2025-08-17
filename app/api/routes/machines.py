from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...schemas.machine import MachineCreate, MachineOut, ProductionEventCreate, ProductionEventOut
from ...models.machine import Machine, ProductionEvent, StopReason
from ..deps import get_db, require_roles
from ...models.user import UserRole

router = APIRouter()


@router.post("/", response_model=MachineOut, dependencies=[Depends(require_roles(UserRole.admin, UserRole.gerente))])
def create_machine(machine_in: MachineCreate, db: Session = Depends(get_db)):
    existing = db.query(Machine).filter(Machine.name == machine_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nome de máquina já existe")
    machine = Machine(**machine_in.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@router.get("/", response_model=List[MachineOut])
def list_machines(db: Session = Depends(get_db)):
    return db.query(Machine).order_by(Machine.name.asc()).all()


@router.get("/status")
def machines_status(db: Session = Depends(get_db)):
    machines = db.query(Machine).order_by(Machine.name.asc()).all()
    result = []
    for m in machines:
        last_event = (
            db.query(ProductionEvent)
            .filter(ProductionEvent.machine_id == m.id)
            .order_by(desc(ProductionEvent.started_at))
            .first()
        )
        result.append(
            {
                "id": m.id,
                "name": m.name,
                "location": m.location,
                "status": last_event.status if last_event else "unknown",
                "stop_reason": str(last_event.stop_reason) if last_event and last_event.stop_reason else None,
                "last_started_at": last_event.started_at.isoformat() if last_event else None,
                "last_ended_at": last_event.ended_at.isoformat() if last_event and last_event.ended_at else None,
                "last_quantity": last_event.quantity if last_event else 0,
            }
        )
    return result


@router.post("/events", response_model=ProductionEventOut)
def add_event(event_in: ProductionEventCreate, db: Session = Depends(get_db)):
    machine = db.query(Machine).get(event_in.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    event = ProductionEvent(**event_in.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/{machine_id}/stop")
def register_stop(
    machine_id: int,
    reason: StopReason,
    db: Session = Depends(get_db),
):
    machine = db.query(Machine).get(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    now = datetime.utcnow()
    event = ProductionEvent(
        machine_id=machine_id,
        started_at=now,
        ended_at=None,
        status="stopped",
        stop_reason=reason,
        quantity=0,
    )
    db.add(event)
    db.commit()
    return {"ok": True}


@router.get("/{machine_id}/history", response_model=List[ProductionEventOut])
def history(
    machine_id: int,
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(ProductionEvent).filter(ProductionEvent.machine_id == machine_id)
    if start:
        q = q.filter(ProductionEvent.started_at >= start)
    if end:
        q = q.filter((ProductionEvent.ended_at == None) | (ProductionEvent.ended_at <= end))  # noqa: E711
    return q.order_by(ProductionEvent.started_at.desc()).all()
