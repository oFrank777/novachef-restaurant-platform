from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.menu import MenuItemResponse


class CartItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1

    @field_validator("menu_item_id")
    @classmethod
    def validate_menu_item_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id del producto debe ser mayor a 0")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        if v > 99:
            raise ValueError("La cantidad debe ser como máximo 99")
        return v


class CartItemUpdate(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        if v > 99:
            raise ValueError("La cantidad debe ser como máximo 99")
        return v


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    menu_item_id: int
    quantity: int
    added_at: datetime
    menu_item: Optional[MenuItemResponse] = None
