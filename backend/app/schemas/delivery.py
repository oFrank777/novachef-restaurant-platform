import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.sanitizer import contains_sql_injection, sanitize_html


class DeliveryCreate(BaseModel):
    order_id: int
    driver_id: Optional[int] = None
    distance_km: float
    address: str

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id del pedido debe ser mayor a 0")
        return v

    @field_validator("distance_km")
    @classmethod
    def validate_distance_km(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("La distancia debe ser un número finito")
        if v < 0.5:
            raise ValueError("La distancia debe ser al menos 0.5 km")
        if v > 20.0:
            raise ValueError("La distancia debe ser como máximo 20.0 km")
        return round(v, 2)

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("La dirección debe tener al menos 5 caracteres")
        if len(v) > 200:
            raise ValueError("La dirección debe tener como máximo 200 caracteres")
        if contains_sql_injection(v):
            raise ValueError("La dirección contiene contenido potencialmente malicioso")
        return sanitize_html(v)


VALID_DELIVERY_STATUSES = ["ASIGNADO", "RECOGIDO", "EN_TRANSITO", "ENTREGADO"]

VALID_DELIVERY_TRANSITIONS = {
    "ASIGNADO": ["RECOGIDO", "ENTREGADO"],
    "RECOGIDO": ["EN_TRANSITO", "ENTREGADO"],
    "EN_TRANSITO": ["ENTREGADO"],
    "ENTREGADO": [],
}


class DeliveryUpdate(BaseModel):
    status: Optional[str] = None
    driver_id: Optional[int] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().upper()
        if v not in VALID_DELIVERY_STATUSES:
            raise ValueError(
                f"El estado debe ser uno de: {', '.join(VALID_DELIVERY_STATUSES)}"
            )
        return v


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    driver_id: Optional[int] = None
    distance_km: float
    delivery_cost: float
    status: str
    address: str
    estimated_minutes: Optional[int] = None
    created_at: datetime
