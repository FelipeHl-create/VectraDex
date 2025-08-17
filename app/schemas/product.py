from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    quantity: int
    unit: str
    location: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    location: Optional[str] = None


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True
