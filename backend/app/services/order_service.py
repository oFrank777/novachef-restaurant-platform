from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models.cart import CartItem
from app.models.delivery import Delivery
from app.models.inventory import Inventory
from app.models.menu import MenuItem
from app.models.order import VALID_TRANSITIONS, Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate
from app.utils.exceptions import BadRequestError, ForbiddenError, NotFoundError


def _is_pickup_order(order: Order) -> bool:
    if not order.delivery_address:
        return True
    return order.delivery_address.strip().lower() in (
        "recojo en local",
        "recogida en local",
    )


def _is_delivery_order(order: Order) -> bool:
    return not _is_pickup_order(order)


def _role_can_transition(role: str, current: str, new: str, order: Order) -> bool:
    if role == "admin":
        return True
    if role == "cajero":
        cajero_allowed = {
            ("PENDIENTE", "PREPARANDO"),
            ("PENDIENTE", "CANCELADO"),
            ("PREPARANDO", "LISTO"),
            ("PREPARANDO", "CANCELADO"),
            ("LISTO", "CANCELADO"),
        }
        if (current, new) in cajero_allowed:
            return True
        if current == "LISTO" and new == "ENTREGADO":
            return _is_pickup_order(order)
        return False
    if role == "delivery":
        if not _is_delivery_order(order):
            return False
        return (current, new) in {
            ("LISTO", "RECOGIDO"),
            ("RECOGIDO", "ENVIADO"),
            ("ENVIADO", "ENTREGADO"),
        }
    return False


def _ensure_delivery_record(db: Session, order: Order) -> None:
    """Crea registro de entrega cuando un pedido a domicilio queda LISTO."""
    if not _is_delivery_order(order):
        return
    existing = db.query(Delivery).filter(Delivery.order_id == order.id).first()
    if existing:
        return
    distance_km = 3.0
    delivery_cost = round(
        settings.BASE_DELIVERY_FEE + (distance_km * settings.DELIVERY_RATE_PER_KM),
        2,
    )
    db.add(
        Delivery(
            order_id=order.id,
            driver_id=None,
            distance_km=distance_km,
            delivery_cost=delivery_cost,
            status="ASIGNADO",
            address=order.delivery_address,
            estimated_minutes=int(10 + distance_km * 3),
        )
    )


def _assign_delivery_driver(db: Session, order_id: int, driver_id: int) -> None:
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if delivery and delivery.driver_id is None:
        delivery.driver_id = driver_id


def _restore_inventory_on_cancel(db: Session, order: Order) -> None:
    for item in order.items:
        inventory = (
            db.query(Inventory)
            .filter(Inventory.menu_item_id == item.menu_item_id)
            .first()
        )
        if inventory:
            inventory.stock += item.quantity


def list_orders_for_user(
    db: Session,
    user: User,
    status: Optional[str] = None,
) -> List[Order]:
    """Pedidos visibles según el rol operativo del usuario."""
    if user.role in ("admin", "cajero"):
        return get_orders(db, user_id=None, status=status)
    if user.role == "delivery":
        orders = get_orders(db, user_id=None, status=status)
        visible = []
        for o in orders:
            if not _is_delivery_order(o):
                continue
            delivery = db.query(Delivery).filter(Delivery.order_id == o.id).first()
            if o.status in ("PENDIENTE", "PREPARANDO"):
                visible.append(o)
            elif o.status == "LISTO" and (
                delivery is None or delivery.driver_id is None or delivery.driver_id == user.id
            ):
                visible.append(o)
            elif delivery and delivery.driver_id == user.id:
                visible.append(o)
        return visible
    return get_orders(db, user_id=user.id, status=status)


def user_can_view_order(user: User, order: Order, db: Session | None = None) -> bool:
    if user.role in ("admin", "cajero"):
        return True
    if user.role == "delivery":
        if not _is_delivery_order(order):
            return False
        if db is None:
            return True
        delivery = db.query(Delivery).filter(Delivery.order_id == order.id).first()
        if order.status in ("PENDIENTE", "PREPARANDO"):
            return True
        if order.status == "LISTO":
            return delivery is None or delivery.driver_id in (None, user.id)
        return delivery is not None and delivery.driver_id == user.id
    return order.user_id == user.id


def _assert_delivery_can_transition(
    db: Session, order: Order, user_id: int, new_status: str
) -> None:
    delivery = db.query(Delivery).filter(Delivery.order_id == order.id).first()
    if new_status == "RECOGIDO":
        if delivery and delivery.driver_id not in (None, user_id):
            raise ForbiddenError(detail="Esta entrega ya está asignada a otro repartidor")
        return
    if new_status in ("ENVIADO", "ENTREGADO"):
        if not delivery or delivery.driver_id != user_id:
            raise ForbiddenError(detail="No tienes permiso para actualizar esta entrega")


def create_order(db: Session, user_id: int, order_data: OrderCreate) -> Order:
    """
    Create an order from the user's cart.
    - Validates cart is not empty
    - Calculates total from current menu prices
    - Creates order items with unit prices snapshotted at time of order
    - Deducts inventory stock
    - Clears the user's cart
    """
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.menu_item))
        .filter(CartItem.user_id == user_id)
        .all()
    )

    if not cart_items:
        raise BadRequestError(detail="El carrito está vacío. Añade productos antes de realizar un pedido.")
    total_amount = 0.0
    order_items_data = []

    for cart_item in cart_items:
        menu_item = cart_item.menu_item
        if not menu_item:
            raise BadRequestError(
                detail=f"El producto con id {cart_item.menu_item_id} ya no existe"
            )
        if not menu_item.is_available:
            raise BadRequestError(
                detail=f"El producto '{menu_item.name}' ya no está disponible"
            )
        inventory = (
            db.query(Inventory)
            .filter(Inventory.menu_item_id == menu_item.id)
            .with_for_update()
            .first()
        )
        if inventory and inventory.stock < cart_item.quantity:
            raise BadRequestError(
                detail=f"Stock insuficiente para '{menu_item.name}'. "
                f"Disponible: {inventory.stock}, solicitado: {cart_item.quantity}"
            )

        item_total = menu_item.price * cart_item.quantity
        total_amount += item_total
        order_items_data.append(
            {
                "menu_item_id": menu_item.id,
                "quantity": cart_item.quantity,
                "unit_price": menu_item.price,
            }
        )

    total_amount = round(total_amount, 2)
    
    if total_amount > 5000.00:
        raise BadRequestError(detail="El total del pedido excede el monto máximo permitido ($5000.00)")
    new_order = Order(
        user_id=user_id,
        status="PENDIENTE",
        total_amount=total_amount,
        delivery_address=order_data.delivery_address,
        notes=order_data.notes,
    )
    db.add(new_order)
    db.flush()  
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item_data["menu_item_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.add(order_item)
    for cart_item in cart_items:
        inventory = (
            db.query(Inventory)
            .filter(Inventory.menu_item_id == cart_item.menu_item_id)
            .with_for_update()
            .first()
        )
        if inventory:
            inventory.stock -= cart_item.quantity
            if inventory.stock < 0:
                inventory.stock = 0
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    db.commit()
    db.refresh(new_order)
    return new_order


def get_orders(
    db: Session,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
) -> List[Order]:
    """Retrieve orders with optional filters by user and status."""
    query = db.query(Order).options(joinedload(Order.items))

    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    if status is not None:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).all()


def get_order(db: Session, order_id: int) -> Order:
    """Get a single order by ID with items. Raises NotFoundError if not found."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise NotFoundError(detail=f"Pedido con id {order_id} no encontrado")
    return order


def update_order_status(
    db: Session,
    order_id: int,
    new_status: str,
    *,
    user_role: str,
    user_id: Optional[int] = None,
) -> Order:
    """
    Update an order's status, enforcing the state machine and role permissions.
    """
    order = get_order(db, order_id)
    current_status = order.status

    if not _role_can_transition(user_role, current_status, new_status, order):
        raise ForbiddenError(detail="No tienes permiso para cambiar el estado del pedido")

    if user_role == "delivery" and user_id is not None:
        _assert_delivery_can_transition(db, order, user_id, new_status)

    allowed_transitions = VALID_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_transitions:
        raise BadRequestError(detail="Transición de estado no permitida para este pedido")

    if new_status == "CANCELADO":
        _restore_inventory_on_cancel(db, order)

    order.status = new_status

    if new_status == "LISTO" or (
        new_status in ("RECOGIDO", "ENVIADO", "ENTREGADO") and _is_delivery_order(order)
    ):
        _ensure_delivery_record(db, order)

    if new_status == "RECOGIDO" and user_role == "delivery" and user_id is not None:
        _assign_delivery_driver(db, order.id, user_id)

    db.commit()
    db.refresh(order)
    return order
