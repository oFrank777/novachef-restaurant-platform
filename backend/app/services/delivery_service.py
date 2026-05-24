from sqlalchemy.orm import Session

from app.config import settings
from app.models.delivery import Delivery
from app.models.order import Order
from app.models.user import User
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, VALID_DELIVERY_TRANSITIONS
from app.utils.exceptions import BadRequestError, NotFoundError


def create_delivery(db: Session, delivery_data: DeliveryCreate) -> Delivery:

    order = db.query(Order).filter(Order.id == delivery_data.order_id).first()
    if not order:
        raise NotFoundError(detail=f"Pedido con id {delivery_data.order_id} no encontrado")

    if not order.delivery_address or order.delivery_address.lower() == "recojo en local":
        raise BadRequestError(detail=f"El pedido {order.id} es para recojo en local, no requiere delivery")

    if order.status in ["PENDIENTE", "CANCELADO"]:
        raise BadRequestError(detail=f"No se puede crear entrega para un pedido en estado {order.status}")
    existing_delivery = (
        db.query(Delivery)
        .filter(Delivery.order_id == delivery_data.order_id)
        .first()
    )
    if existing_delivery:
        raise BadRequestError(
            detail=f"La entrega ya existe para el pedido {delivery_data.order_id}"
        )
    delivery_cost = round(
        settings.BASE_DELIVERY_FEE
        + (delivery_data.distance_km * settings.DELIVERY_RATE_PER_KM),
        2,
    )
    estimated_minutes = int(10 + delivery_data.distance_km * 3)
    if delivery_data.driver_id is not None:
        driver = db.query(User).filter(User.id == delivery_data.driver_id).first()
        if not driver:
            raise NotFoundError(
                detail=f"Repartidor con id {delivery_data.driver_id} no encontrado"
            )
        if driver.role != "delivery":
            raise BadRequestError(
                detail=f"Usuario con id {delivery_data.driver_id} no tiene rol de 'delivery'"
            )

    new_delivery = Delivery(
        order_id=delivery_data.order_id,
        driver_id=delivery_data.driver_id,
        distance_km=delivery_data.distance_km,
        delivery_cost=delivery_cost,
        status="ASIGNADO",
        address=delivery_data.address,
        estimated_minutes=estimated_minutes,
    )

    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery


def get_delivery(db: Session, delivery_id: int) -> Delivery:
    """Get a delivery by ID. Raises NotFoundError if not found."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise NotFoundError(detail=f"Entrega con id {delivery_id} no encontrada")
    return delivery


def get_delivery_by_order(db: Session, order_id: int) -> Delivery:
    """Get the delivery associated with an order. Raises NotFoundError if not found."""
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise NotFoundError(
            detail=f"Entrega para el pedido {order_id} no encontrada"
        )
    return delivery


def update_delivery(
    db: Session, delivery_id: int, update_data: DeliveryUpdate
) -> Delivery:
    """Update delivery status and/or driver assignment."""
    delivery = get_delivery(db, delivery_id)

    if update_data.status is not None:
        if update_data.status != delivery.status:
            allowed_next_states = VALID_DELIVERY_TRANSITIONS.get(delivery.status, [])
            if update_data.status not in allowed_next_states:
                raise BadRequestError(
                    detail=f"No se puede transicionar la entrega de {delivery.status} a {update_data.status}"
                )
            delivery.status = update_data.status

    if update_data.driver_id is not None:
        driver = db.query(User).filter(User.id == update_data.driver_id).first()
        if not driver:
            raise NotFoundError(
                detail=f"Repartidor con id {update_data.driver_id} no encontrado"
            )
        if driver.role != "delivery":
            raise BadRequestError(
                detail=f"Usuario con id {update_data.driver_id} no tiene rol de 'delivery'"
            )
        delivery.driver_id = update_data.driver_id

    db.commit()
    db.refresh(delivery)
    return delivery


def assign_driver(db: Session, delivery_id: int, driver_id: int) -> Delivery:
    """Assign a driver to a delivery. The driver must have role 'delivery'."""
    delivery = get_delivery(db, delivery_id)

    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver:
        raise NotFoundError(detail=f"Repartidor con id {driver_id} no encontrado")
    if driver.role != "delivery":
        raise BadRequestError(
            detail=f"Usuario con id {driver_id} no tiene rol de 'delivery'"
        )

    delivery.driver_id = driver_id
    db.commit()
    db.refresh(delivery)
    return delivery

def get_all_deliveries(
    db: Session,
    driver_id: int | None = None,
    *,
    include_unassigned: bool = False,
):
    """Get all deliveries, optionally filtered by driver."""
    query = db.query(Delivery)
    if driver_id is not None:
        if include_unassigned:
            from sqlalchemy import or_

            query = query.filter(
                or_(Delivery.driver_id == driver_id, Delivery.driver_id.is_(None))
            )
        else:
            query = query.filter(Delivery.driver_id == driver_id)
    return query.order_by(Delivery.created_at.desc()).all()
