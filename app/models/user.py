from sqlalchemy import Column, Integer, String, Enum
from ..db.base import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    operador = "operador"
    gerente = "gerente"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.operador, nullable=False)
