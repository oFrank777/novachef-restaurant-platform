from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(30), nullable=False)
    image_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    cart_items = relationship(
        "CartItem", back_populates="menu_item", cascade="all, delete-orphan"
    )
    order_items = relationship("OrderItem", back_populates="menu_item")
    inventory = relationship(
        "Inventory", back_populates="menu_item", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"
