from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    card_last_four = Column(String(4), nullable=False)
    status = Column(String(20), nullable=False, default="PENDIENTE")
    payment_method = Column(String(20), default="credit_card")
    processed_at = Column(DateTime, nullable=True)
    order = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, order_id={self.order_id}, "
            f"status='{self.status}', amount={self.amount})>"
        )
