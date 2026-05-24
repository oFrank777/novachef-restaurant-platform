from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    distance_km = Column(Float, nullable=False)
    delivery_cost = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="ASIGNADO")
    address = Column(String(200), nullable=False)
    estimated_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    order = relationship("Order", back_populates="delivery")
    driver = relationship("User", back_populates="deliveries")

    def __repr__(self) -> str:
        return (
            f"<Delivery(id={self.id}, order_id={self.order_id}, "
            f"status='{self.status}')>"
        )
