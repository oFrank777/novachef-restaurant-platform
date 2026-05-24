from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services import order_service
from app.models.order import VALID_ORDER_STATES
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException, ForbiddenError

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.create_order(db, current_user.id, order_data)
        return order
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if status is not None:
            status = status.strip().upper()
            if status not in VALID_ORDER_STATES:
                from app.utils.exceptions import BadRequestError
                raise BadRequestError(detail="Estado de pedido inválido")
        orders = order_service.list_orders_for_user(db, current_user, status=status)
        return orders
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.get_order(db, order_id)
        if not order_service.user_can_view_order(current_user, order, db):
            raise ForbiddenError(detail="No tienes permiso para ver este pedido")
        return order
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "cajero", "delivery")),
):
    try:
        order = order_service.update_order_status(
            db,
            order_id,
            status_update.status,
            user_role=current_user.role,
            user_id=current_user.id,
        )
        return order
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)
