from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from app.services import inventory_service
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/low-stock", response_model=List[InventoryResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "cajero")),
):
    try:
        items = inventory_service.get_low_stock_items(db)
        return items
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )


@router.get("/", response_model=List[InventoryResponse])
def list_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "cajero")),
):
    try:
        items = inventory_service.get_all_inventory(db)
        return items
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )


@router.get("/{inv_id}", response_model=InventoryResponse)
def get_inventory(
    inv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "cajero")),
):
    try:
        inventory = inventory_service.get_inventory(db, inv_id)
        return inventory
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )


@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory(
    inv_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        inventory = inventory_service.create_inventory(db, inv_data)
        return inventory
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )


@router.put("/{inv_id}", response_model=InventoryResponse)
def update_inventory(
    inv_id: int,
    update_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        inventory = inventory_service.update_inventory(db, inv_id, update_data)
        return inventory
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )
