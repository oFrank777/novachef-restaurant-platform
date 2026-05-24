from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="cliente")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    orders = relationship("Order", back_populates="user", lazy="dynamic")
    cart_items = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    deliveries = relationship("Delivery", back_populates="driver", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
