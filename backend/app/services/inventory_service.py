from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models.inventory import Inventory
from app.models.menu import MenuItem
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.utils.exceptions import BadRequestError, ConflictError, NotFoundError


def create_inventory(db: Session, inv_data: InventoryCreate) -> Inventory:
    """Create an inventory record for a menu item."""
    menu_item = db.query(MenuItem).filter(MenuItem.id == inv_data.menu_item_id).first()
    if not menu_item:
        raise NotFoundError(
            detail=f"Producto con id {inv_data.menu_item_id} no encontrado"
        )
    existing = (
        db.query(Inventory)
        .filter(Inventory.menu_item_id == inv_data.menu_item_id)
        .first()
    )
    if existing:
        raise ConflictError(
            detail=f"El inventario ya existe para el producto {inv_data.menu_item_id}"
        )

    new_inventory = Inventory(
        menu_item_id=inv_data.menu_item_id,
        stock=inv_data.stock,
        min_stock=inv_data.min_stock,
    )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory


def get_inventory(db: Session, inv_id: int) -> Inventory:
    """Get inventory by ID with eager-loaded menu item. Raises NotFoundError if not found."""
    inventory = (
        db.query(Inventory)
        .options(joinedload(Inventory.menu_item))
        .filter(Inventory.id == inv_id)
        .first()
    )
    if not inventory:
        raise NotFoundError(detail=f"Inventario con id {inv_id} no encontrado")
    return inventory


def get_all_inventory(db: Session) -> List[Inventory]:
    """Get all inventory records with their menu items."""
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.menu_item))
        .all()
    )


def update_inventory(
    db: Session, inv_id: int, update_data: InventoryUpdate
) -> Inventory:
    """Update inventory stock and/or min_stock. Prevents stock from going negative."""
    inventory = get_inventory(db, inv_id)

    if update_data.stock is not None:
        if update_data.stock < 0:
            raise BadRequestError(detail="El stock no puede ser negativo")
        inventory.stock = update_data.stock

    if update_data.min_stock is not None:
        if update_data.min_stock < 0:
            raise BadRequestError(detail="El stock mínimo no puede ser negativo")
        inventory.min_stock = update_data.min_stock

    db.commit()
    db.refresh(inventory)
    return inventory


def deduct_stock(db: Session, menu_item_id: int, quantity: int) -> Inventory:
    """
    Atomically deduct stock for a menu item.
    Raises BadRequestError if insufficient stock.
    """
    inventory = (
        db.query(Inventory)
        .filter(Inventory.menu_item_id == menu_item_id)
        .first()
    )
    if not inventory:
        raise NotFoundError(
            detail=f"Inventario para el producto {menu_item_id} no encontrado"
        )

    if inventory.stock < quantity:
        raise BadRequestError(
            detail=f"Stock insuficiente para el producto {menu_item_id}. "
            f"Available: {inventory.stock}, requested: {quantity}"
        )

    inventory.stock -= quantity
    db.commit()
    db.refresh(inventory)
    return inventory


def get_low_stock_items(db: Session) -> List[Inventory]:
    """Return inventory items where stock <= min_stock."""
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.menu_item))
        .filter(Inventory.stock <= Inventory.min_stock)
        .all()
    )
