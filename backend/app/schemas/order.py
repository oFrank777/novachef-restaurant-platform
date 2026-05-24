from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.sanitizer import sanitize_html, contains_sql_injection
from app.models.order import VALID_ORDER_STATES


class OrderCreate(BaseModel):
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("delivery_address")
    @classmethod
    def validate_delivery_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) < 5:
            raise ValueError("La dirección de entrega debe tener al menos 5 caracteres")
        if len(v) > 200:
            raise ValueError("La dirección de entrega debe tener como máximo 200 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La dirección contiene contenido potencialmente malicioso")
        return sanitize_html(v)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError("Las notas deben tener como máximo 500 caracteres")
        if contains_sql_injection(v):
            raise ValueError("Las notas contienen contenido potencialmente malicioso")
        return sanitize_html(v)


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_ORDER_STATES:
            raise ValueError(
                f"El estado debe ser uno de: {', '.join(VALID_ORDER_STATES)}"
            )
        return v


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    total_amount: float
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
