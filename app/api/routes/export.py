from io import StringIO, BytesIO
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from ...models.product import Product
from ...models.machine import ProductionEvent
from ..deps import get_db

router = APIRouter()


@router.get("/products/csv")
def export_products_csv(db: Session = Depends(get_db)):
    rows = db.query(Product).all()
    data = [
        {
            "id": r.id,
            "code": r.code,
            "name": r.name,
            "description": r.description,
            "quantity": r.quantity,
            "unit": r.unit,
            "location": r.location,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    csv_buf = StringIO()
    df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    return StreamingResponse(csv_buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=products.csv"})


@router.get("/products/xlsx")
def export_products_xlsx(db: Session = Depends(get_db)):
    rows = db.query(Product).all()
    data = [
        {
            "id": r.id,
            "code": r.code,
            "name": r.name,
            "description": r.description,
            "quantity": r.quantity,
            "unit": r.unit,
            "location": r.location,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="products", index=False)
    out.seek(0)
    return StreamingResponse(out, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=products.xlsx"})


@router.get("/production/csv")
def export_production_csv(db: Session = Depends(get_db)):
    rows = db.query(ProductionEvent).all()
    data = [
        {
            "id": r.id,
            "machine_id": r.machine_id,
            "started_at": r.started_at,
            "ended_at": r.ended_at,
            "status": r.status,
            "stop_reason": str(r.stop_reason) if r.stop_reason else None,
            "quantity": r.quantity,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    csv_buf = StringIO()
    df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    return StreamingResponse(csv_buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=production.csv"})


@router.get("/production/xlsx")
def export_production_xlsx(db: Session = Depends(get_db)):
    rows = db.query(ProductionEvent).all()
    data = [
        {
            "id": r.id,
            "machine_id": r.machine_id,
            "started_at": r.started_at,
            "ended_at": r.ended_at,
            "status": r.status,
            "stop_reason": str(r.stop_reason) if r.stop_reason else None,
            "quantity": r.quantity,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="production", index=False)
    out.seek(0)
    return StreamingResponse(out, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=production.xlsx"})
