from sqlalchemy import Column, Integer, String, Text
from ..db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=0, nullable=False)
    unit = Column(String(16), default="un", nullable=False)
    location = Column(String(64), nullable=True)
