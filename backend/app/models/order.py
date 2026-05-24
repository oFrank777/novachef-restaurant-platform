from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
VALID_ORDER_STATES = ["PENDIENTE", "PREPARANDO", "LISTO", "RECOGIDO", "ENVIADO", "ENTREGADO", "CANCELADO"]
VALID_TRANSITIONS = {
    "PENDIENTE": ["PREPARANDO", "CANCELADO"],
    "PREPARANDO": ["LISTO", "CANCELADO"],
    "LISTO": ["RECOGIDO", "ENTREGADO", "CANCELADO"],
    "RECOGIDO": ["ENVIADO"],
    "ENVIADO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PENDIENTE")
    total_amount = Column(Float, nullable=False)
    delivery_address = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    delivery = relationship(
        "Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    payment = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, user_id={self.user_id}, "
            f"status='{self.status}', total={self.total_amount})>"
        )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"menu_item_id={self.menu_item_id}, qty={self.quantity})>"
        )
