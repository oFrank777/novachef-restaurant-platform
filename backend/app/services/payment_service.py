from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate
from app.utils.exceptions import BadRequestError, NotFoundError, ForbiddenError


def process_payment(db: Session, payment_data: PaymentCreate, current_user_id: int) -> Payment:
    """
    Process a payment for an order.
    - Validates order exists and belongs to user
    - Ensures order is PENDIENTE
    - Ensures order hasn't already been paid
    - Validates payment amount matches order total
    - Stores only last 4 digits of card number
    """
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise NotFoundError(
            detail=f"Pedido con id {payment_data.order_id} no encontrado"
        )
        
    if order.user_id != current_user_id:
        raise ForbiddenError(detail="Solo puedes pagar tus propios pedidos")
        
    if order.status != "PENDIENTE":
        raise BadRequestError(detail=f"No se puede pagar un pedido en estado {order.status}")
    existing_payment = (
        db.query(Payment)
        .filter(Payment.order_id == payment_data.order_id)
        .first()
    )
    if existing_payment:
        raise BadRequestError(
            detail=f"El pago ya existe para el pedido {payment_data.order_id}"
        )
    expected_amount = round(order.total_amount, 2)
    provided_amount = round(payment_data.amount, 2)
    if abs(provided_amount - expected_amount) > 0.01:
        raise BadRequestError(detail="El monto del pago no coincide con el total del pedido")
    if payment_data.payment_method == "cash":
        card_last_four = "CASH"
    else:
        card_last_four = payment_data.card_number[-4:]

    new_payment = Payment(
        order_id=payment_data.order_id,
        amount=provided_amount,
        card_last_four=card_last_four,
        status="COMPLETED",
        payment_method=payment_data.payment_method,
        processed_at=datetime.now(timezone.utc),
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


def get_payment(db: Session, payment_id: int) -> Payment:
    """Get a payment by ID. Raises NotFoundError if not found."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise NotFoundError(detail=f"Pago con id {payment_id} no encontrado")
    return payment


def get_payment_by_order(db: Session, order_id: int) -> Payment:
    """Get the payment associated with an order. Raises NotFoundError if not found."""
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise NotFoundError(
            detail=f"Pago para el pedido {order_id} no encontrado"
        )
    return payment

def get_all_payments(db: Session):
    """Get all payments."""
    return db.query(Payment).all()


def user_can_view_payment(db: Session, user_id: int, user_role: str, payment: Payment) -> bool:
    if user_role in ("admin", "cajero"):
        return True
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    return order is not None and order.user_id == user_id
