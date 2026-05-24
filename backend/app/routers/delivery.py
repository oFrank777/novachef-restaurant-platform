from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.delivery import DeliveryCreate, DeliveryResponse, DeliveryUpdate
from app.services import delivery_service
from app.services.access_control import assert_delivery_access
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException, ForbiddenError

router = APIRouter(prefix="/api/delivery", tags=["Delivery"])


@router.get("/", response_model=List[DeliveryResponse])
def list_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "delivery")),
):
    try:
        if current_user.role == "delivery":
            deliveries = delivery_service.get_all_deliveries(
                db, driver_id=current_user.id, include_unassigned=True
            )
        else:
            deliveries = delivery_service.get_all_deliveries(db)
        return deliveries
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.post("/", response_model=DeliveryResponse, status_code=201)
def create_delivery(
    delivery_data: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        delivery = delivery_service.create_delivery(db, delivery_data)
        return delivery
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delivery = delivery_service.get_delivery(db, delivery_id)
        assert_delivery_access(db, current_user, delivery)
        return delivery
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/order/{order_id}", response_model=DeliveryResponse)
def get_delivery_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delivery = delivery_service.get_delivery_by_order(db, order_id)
        assert_delivery_access(db, current_user, delivery)
        return delivery
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    update_data: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "delivery")),
):
    try:
        delivery = delivery_service.get_delivery(db, delivery_id)
        if current_user.role == "delivery":
            if (
                delivery.driver_id is not None
                and delivery.driver_id != current_user.id
            ):
                raise ForbiddenError(detail="No tienes permiso para actualizar esta entrega")
            if update_data.driver_id is not None and update_data.driver_id != current_user.id:
                raise ForbiddenError(detail="No puedes reasignar entregas a otros repartidores")
            if update_data.driver_id is None and delivery.driver_id is None:
                update_data = update_data.model_copy(update={"driver_id": current_user.id})

        delivery = delivery_service.update_delivery(db, delivery_id, update_data)
        return delivery
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)
