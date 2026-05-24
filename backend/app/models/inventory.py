from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(
        Integer, ForeignKey("menu_items.id"), unique=True, nullable=False
    )
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=5)
    last_updated = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    menu_item = relationship("MenuItem", back_populates="inventory")

    def __repr__(self) -> str:
        return (
            f"<Inventory(id={self.id}, menu_item_id={self.menu_item_id}, "
            f"stock={self.stock})>"
        )
