from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.menu import MenuItem
from app.schemas.menu import MenuItemCreate, MenuItemUpdate
from app.utils.exceptions import NotFoundError


def create_menu_item(db: Session, item_data: MenuItemCreate) -> MenuItem:
    """Create a new menu item."""
    new_item = MenuItem(
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        category=item_data.category,
        image_url=item_data.image_url,
        is_available=item_data.is_available,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def get_all_menu_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    available_only: bool = False,
) -> List[MenuItem]:
    """Retrieve menu items with optional category filter and pagination."""
    query = db.query(MenuItem)

    if category:
        query = query.filter(MenuItem.category == category)
    if available_only:
        query = query.filter(MenuItem.is_available == True)

    return query.offset(skip).limit(limit).all()


def get_menu_item(db: Session, item_id: int) -> MenuItem:
    """Get a single menu item by ID. Raises NotFoundError if not found."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise NotFoundError(detail=f"Producto con id {item_id} no encontrado")
    return item


def update_menu_item(db: Session, item_id: int, item_data: MenuItemUpdate) -> MenuItem:
    """Update a menu item. Only supplied (non-None) fields are updated."""
    item = get_menu_item(db, item_id)

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_menu_item(db: Session, item_id: int) -> None:
    """Delete a menu item by ID. Raises NotFoundError if not found."""
    item = get_menu_item(db, item_id)
    db.delete(item)
    db.commit()
