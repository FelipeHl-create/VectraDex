from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...schemas.product import ProductCreate, ProductOut, ProductUpdate
from ...models.product import Product
from ..deps import get_db, require_roles
from ...models.user import UserRole

router = APIRouter()


@router.post("/", response_model=ProductOut, dependencies=[Depends(require_roles(UserRole.admin, UserRole.gerente))])
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.code == product_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código já existe")
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None),
    skip: int = 0,
    limit: int = Query(default=20, le=100),
):
    query = db.query(Product)
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.code.ilike(like)))
    items = query.order_by(Product.name.asc()).offset(skip).limit(limit).all()
    return items


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_roles(UserRole.admin, UserRole.gerente))])
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", dependencies=[Depends(require_roles(UserRole.admin))])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(product)
    db.commit()
    return {"ok": True}


@router.post("/{product_id}/decrement")
def decrement_after_label(product_id: int, qty: int = 1, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if product.quantity < qty:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque")
    product.quantity -= qty
    db.add(product)
    db.commit()
    return {"id": product.id, "quantity": product.quantity}
