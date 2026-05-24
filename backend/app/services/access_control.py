from sqlalchemy.orm import Session

from app.models.delivery import Delivery
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.utils.exceptions import ForbiddenError


def user_can_access_order(user: User, order: Order) -> bool:
    if user.role in ("admin", "cajero"):
        return True
    if user.role == "delivery":
        return bool(order.delivery_address) and order.delivery_address.strip().lower() not in (
            "recojo en local",
            "recogida en local",
        )
    return order.user_id == user.id


def assert_payment_access(db: Session, user: User, payment: Payment) -> None:
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if user.role in ("admin", "cajero"):
        return
    if order and order.user_id == user.id:
        return
    raise ForbiddenError(detail="No tienes permiso para ver este pago")


def assert_order_payment_access(db: Session, user: User, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    if user.role in ("admin", "cajero"):
        return order
    if order.user_id == user.id:
        return order
    raise ForbiddenError(detail="No tienes permiso para ver este pago")


def assert_delivery_access(db: Session, user: User, delivery: Delivery) -> None:
    if user.role == "admin":
        return
    if user.role == "delivery":
        if delivery.driver_id is None or delivery.driver_id == user.id:
            return
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if order and order.user_id == user.id:
        return
    raise ForbiddenError(detail="No tienes permiso para ver esta entrega")


def assert_delivery_order_access(db: Session, user: User, order_id: int) -> None:
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise ForbiddenError(detail="No tienes permiso para ver esta entrega")
    assert_delivery_access(db, user, delivery)
