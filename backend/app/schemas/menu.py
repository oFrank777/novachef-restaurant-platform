import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.sanitizer import contains_sql_injection, sanitize_html
import re


class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        if len(v) > 50:
            raise ValueError("El nombre debe tener como máximo 50 caracteres")
        if contains_sql_injection(v):
            raise ValueError("El nombre contiene contenido potencialmente malicioso")
        return sanitize_html(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError("La descripción debe tener como máximo 500 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La descripción contiene contenido potencialmente malicioso")
        return sanitize_html(v)

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^https?://", v):
            raise ValueError("La URL de imagen debe ser una URL HTTP/HTTPS válida")
        if contains_sql_injection(v):
            raise ValueError("La URL de imagen contiene contenido potencialmente malicioso")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("El precio debe ser un número finito")
        if v < 0.01:
            raise ValueError("El precio debe ser al menos 0.01")
        if v > 999.99:
            raise ValueError("El precio debe ser como máximo 999.99")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("La categoría debe tener al menos 2 caracteres")
        if len(v) > 30:
            raise ValueError("La categoría debe tener como máximo 30 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La categoría contiene contenido potencialmente malicioso")
        return sanitize_html(v)


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        if len(v) > 50:
            raise ValueError("El nombre debe tener como máximo 50 caracteres")
        if contains_sql_injection(v):
            raise ValueError("El nombre contiene contenido potencialmente malicioso")
        return sanitize_html(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError("La descripción debe tener como máximo 500 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La descripción contiene contenido potencialmente malicioso")
        return sanitize_html(v)

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^https?://", v):
            raise ValueError("La URL de imagen debe ser una URL HTTP/HTTPS válida")
        if contains_sql_injection(v):
            raise ValueError("La URL de imagen contiene contenido potencialmente malicioso")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if not math.isfinite(v):
            raise ValueError("El precio debe ser un número finito")
        if v < 0.01:
            raise ValueError("El precio debe ser al menos 0.01")
        if v > 999.99:
            raise ValueError("El precio debe ser como máximo 999.99")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("La categoría debe tener al menos 2 caracteres")
        if len(v) > 30:
            raise ValueError("La categoría debe tener como máximo 30 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La categoría contiene contenido potencialmente malicioso")
        return sanitize_html(v)


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool
    created_at: datetime
