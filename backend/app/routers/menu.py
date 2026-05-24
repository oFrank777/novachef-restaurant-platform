from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.schemas.menu import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services import menu_service
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/", response_model=List[MenuItemResponse])
def list_menu_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum items to return"),
    available_only: bool = Query(False, description="Show only available items"),
    db: Session = Depends(get_db),
):
    try:
        items = menu_service.get_all_menu_items(
            db, skip=skip, limit=limit, category=category, available_only=available_only
        )
        return items
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = menu_service.get_menu_item(db, item_id)
        return item
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.post("/", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    item_data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        item = menu_service.create_menu_item(db, item_data)
        return item
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        item = menu_service.update_menu_item(db, item_id, item_data)
        return item
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.delete("/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        menu_service.delete_menu_item(db, item_id)
        return None
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)
