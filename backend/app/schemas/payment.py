import math
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.config import settings


class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    card_number: Optional[str] = None
    cvv: Optional[str] = None
    payment_method: str = "credit_card"

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id del pedido debe ser mayor a 0")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("El monto debe ser un número finito")
        if v < 0.01:
            raise ValueError("El monto debe ser al menos 0.01")
        if v > 5000.00:
            raise ValueError("El monto debe ser como máximo 5000.00")
        return round(v, 2)

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in settings.ALLOWED_PAYMENT_METHODS:
            raise ValueError(
                f"El método de pago debe ser uno de: {', '.join(settings.ALLOWED_PAYMENT_METHODS)}"
            )
        return v

    @model_validator(mode="after")
    def validate_card_or_cash(self):
        if self.payment_method == "cash":
            return self
        if not self.card_number or not self.cvv:
            raise ValueError("Número de tarjeta y CVV son obligatorios para pagos con tarjeta")
        card = self.card_number.strip()
        if not re.match(r"^\d{16}$", card):
            raise ValueError("El número de tarjeta debe tener exactamente 16 dígitos")
        total = 0
        reverse_digits = [int(x) for x in card[::-1]]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        if total % 10 != 0:
            raise ValueError("Número de tarjeta inválido")
        cvv = self.cvv.strip()
        if not re.match(r"^\d{3}$", cvv):
            raise ValueError("El CVV debe tener exactamente 3 dígitos")
        self.card_number = card
        self.cvv = cvv
        return self


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: float
    card_last_four: str
    status: str
    payment_method: str
    processed_at: Optional[datetime] = None
