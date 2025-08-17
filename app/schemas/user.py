from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.operador


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
