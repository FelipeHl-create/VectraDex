from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...models.machine import ProductionEvent, StopReason
from ...models.product import Product
from ..deps import get_db

router = APIRouter()


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    window_start = now - timedelta(days=7)

    total_stock = db.query(func.sum(Product.quantity)).scalar() or 0

    total_operating_time = db.query(
        func.sum(func.julianday(func.coalesce(ProductionEvent.ended_at, now)) - func.julianday(ProductionEvent.started_at))
    ).filter(ProductionEvent.status == "operating", ProductionEvent.started_at >= window_start).scalar() or 0

    total_stopped_time = db.query(
        func.sum(func.julianday(func.coalesce(ProductionEvent.ended_at, now)) - func.julianday(ProductionEvent.started_at))
    ).filter(ProductionEvent.status == "stopped", ProductionEvent.started_at >= window_start).scalar() or 0

    produced_qty = db.query(func.sum(ProductionEvent.quantity)).filter(
        ProductionEvent.started_at >= window_start
    ).scalar() or 0

    reasons = (
        db.query(ProductionEvent.stop_reason, func.count(ProductionEvent.id))
        .filter(ProductionEvent.status == "stopped", ProductionEvent.started_at >= window_start)
        .group_by(ProductionEvent.stop_reason)
        .all()
    )
    reasons_dict = {str(reason or "none"): count for reason, count in reasons}

    return {
        "total_stock": total_stock,
        "total_operating_time_days": total_operating_time,
        "total_stopped_time_days": total_stopped_time,
        "produced_qty": produced_qty,
        "stop_reasons": reasons_dict,
    }


@router.get("/timeseries")

def timeseries(
    db: Session = Depends(get_db),
    days: int = Query(default=14, ge=1, le=90),
):
    now = datetime.utcnow()
    start = now - timedelta(days=days)
    # Produção por dia
    rows = (
        db.query(
            func.date(ProductionEvent.started_at),
            func.sum(ProductionEvent.quantity),
        )
        .filter(ProductionEvent.started_at >= start)
        .group_by(func.date(ProductionEvent.started_at))
        .order_by(func.date(ProductionEvent.started_at))
        .all()
    )
    labels = [r[0] for r in rows]
    values = [int(r[1] or 0) for r in rows]
    # Paradas por dia
    stop_rows = (
        db.query(
            func.date(ProductionEvent.started_at),
            func.count(ProductionEvent.id),
        )
        .filter(ProductionEvent.started_at >= start, ProductionEvent.status == "stopped")
        .group_by(func.date(ProductionEvent.started_at))
        .order_by(func.date(ProductionEvent.started_at))
        .all()
    )
    stop_labels = [r[0] for r in stop_rows]
    stop_values = [int(r[1] or 0) for r in stop_rows]
    return {
        "produced": {"labels": labels, "values": values},
        "stops": {"labels": stop_labels, "values": stop_values},
    }
