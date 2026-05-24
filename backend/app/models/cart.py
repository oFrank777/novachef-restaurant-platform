from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="cart_items")
    menu_item = relationship("MenuItem", back_populates="cart_items")

    def __repr__(self) -> str:
        return (
            f"<CartItem(id={self.id}, user_id={self.user_id}, "
            f"menu_item_id={self.menu_item_id}, qty={self.quantity})>"
        )
