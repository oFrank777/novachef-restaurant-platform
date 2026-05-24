from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import payment_service
from app.models.order import Order
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException, ForbiddenError, NotFoundError

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "cajero")),
):
    try:
        payments = payment_service.get_all_payments(db)
        return payments
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.post("/", response_model=PaymentResponse, status_code=201)
def process_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payment = payment_service.process_payment(db, payment_data, current_user.id)
        return payment
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payment = payment_service.get_payment(db, payment_id)
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if not order:
            raise NotFoundError(detail="Pedido no encontrado")
        if current_user.role not in ("admin", "cajero") and order.user_id != current_user.id:
            raise ForbiddenError(detail="No tienes permiso para ver este pago")
        return payment
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError(detail="Pedido no encontrado")
        if current_user.role not in ("admin", "cajero") and order.user_id != current_user.id:
            raise ForbiddenError(detail="No tienes permiso para ver este pago")
        payment = payment_service.get_payment_by_order(db, order_id)
        return payment
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)
