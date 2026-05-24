import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.utils.sanitizer import contains_sql_injection


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "cliente"

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")
        if len(v) > 30:
            raise ValueError("El usuario debe tener como máximo 30 caracteres")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "El usuario solo puede contener letras, números y guiones bajos"
            )
        if contains_sql_injection(v):
            raise ValueError("El usuario contiene contenido potencialmente malicioso")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre/apellido debe tener al menos 2 caracteres")
        if len(v) > 50:
            raise ValueError("El nombre/apellido debe tener como máximo 50 caracteres")
        if contains_sql_injection(v):
            raise ValueError("El nombre/apellido contiene contenido potencialmente malicioso")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        from app.config import settings

        if len(v) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"La contraseña debe tener al menos {settings.MIN_PASSWORD_LENGTH} caracteres"
            )
        if len(v) > settings.MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"La contraseña debe tener como máximo {settings.MAX_PASSWORD_LENGTH} caracteres"
            )
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> str:
        if v is None:
            return "cliente"
        valid_roles = ["admin", "cliente", "cajero", "delivery"]
        if v not in valid_roles:
            raise ValueError(f"El rol debe ser uno de: {', '.join(valid_roles)}")
        return "cliente"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
