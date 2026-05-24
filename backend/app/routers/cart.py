from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate
from app.services import cart_service
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("/", response_model=List[CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        items = cart_service.get_cart(db, current_user.id)
        return items
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.post("/", response_model=CartItemResponse, status_code=201)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart_item = cart_service.add_to_cart(db, current_user.id, item_data)
        return cart_item
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    update_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart_item = cart_service.update_cart_item(
            db, current_user.id, item_id, update_data
        )
        return cart_item
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.delete("/{item_id}", status_code=204)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart_service.remove_from_cart(db, current_user.id, item_id)
        return None
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.delete("/", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart_service.clear_cart(db, current_user.id)
        return None
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)
