from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.menu import MenuItemResponse


class InventoryCreate(BaseModel):
    menu_item_id: int
    stock: int = 0
    min_stock: int = 5

    @field_validator("menu_item_id")
    @classmethod
    def validate_menu_item_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id del producto debe ser mayor a 0")
        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v: int) -> int:
        if v < 0:
            raise ValueError("El stock debe ser al menos 0")
        if v > 9999:
            raise ValueError("El stock debe ser como máximo 9999")
        return v

    @field_validator("min_stock")
    @classmethod
    def validate_min_stock(cls, v: int) -> int:
        if v < 0:
            raise ValueError("El stock mínimo debe ser al menos 0")
        if v > 999:
            raise ValueError("El stock mínimo debe ser como máximo 999")
        return v


class InventoryUpdate(BaseModel):
    stock: Optional[int] = None
    min_stock: Optional[int] = None

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("El stock debe ser al menos 0")
        if v > 9999:
            raise ValueError("El stock debe ser como máximo 9999")
        return v

    @field_validator("min_stock")
    @classmethod
    def validate_min_stock(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("El stock mínimo debe ser al menos 0")
        if v > 999:
            raise ValueError("El stock mínimo debe ser como máximo 999")
        return v


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    stock: int
    min_stock: int
    last_updated: Optional[datetime] = None
    menu_item: Optional[MenuItemResponse] = None
