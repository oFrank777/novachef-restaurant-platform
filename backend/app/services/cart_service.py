from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models.cart import CartItem
from app.models.inventory import Inventory
from app.models.menu import MenuItem
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.utils.exceptions import BadRequestError, NotFoundError


def add_to_cart(db: Session, user_id: int, item_data: CartItemCreate) -> CartItem:
    """
    Add a menu item to the user's cart.
    If the item is already in the cart, increment the quantity.
    Validates menu item existence, availability, and inventory stock.
    """
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
    if not menu_item:
        raise NotFoundError(detail=f"El producto con id {item_data.menu_item_id} no fue encontrado")
    if not menu_item.is_available:
        raise BadRequestError(detail=f"El producto '{menu_item.name}' no está disponible")
    inventory = (
        db.query(Inventory)
        .filter(Inventory.menu_item_id == item_data.menu_item_id)
        .first()
    )
    if inventory and inventory.stock < item_data.quantity:
        raise BadRequestError(
            detail=f"Stock insuficiente para '{menu_item.name}'. "
            f"Available: {inventory.stock}, requested: {item_data.quantity}"
        )
    existing_cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.menu_item_id == item_data.menu_item_id,
        )
        .first()
    )

    if existing_cart_item:
        new_quantity = existing_cart_item.quantity + item_data.quantity
        if new_quantity > 99:
            raise BadRequestError(detail="La cantidad del carrito no puede exceder 99")
        existing_cart_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    cart_item = CartItem(
        user_id=user_id,
        menu_item_id=item_data.menu_item_id,
        quantity=item_data.quantity,
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def get_cart(db: Session, user_id: int) -> List[CartItem]:
    """Get all cart items for a user with eager-loaded menu items."""
    return (
        db.query(CartItem)
        .options(joinedload(CartItem.menu_item))
        .filter(CartItem.user_id == user_id)
        .all()
    )


def update_cart_item(
    db: Session, user_id: int, cart_item_id: int, update_data: CartItemUpdate
) -> CartItem:
    """Update the quantity of a cart item. User can only update their own items."""
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if not cart_item:
        raise NotFoundError(detail=f"Item del carrito con id {cart_item_id} no encontrado")

    menu_item = db.query(MenuItem).filter(MenuItem.id == cart_item.menu_item_id).first()
    if menu_item and not menu_item.is_available:
        raise BadRequestError(detail=f"El producto '{menu_item.name}' no está disponible")
    inventory = (
        db.query(Inventory)
        .filter(Inventory.menu_item_id == cart_item.menu_item_id)
        .first()
    )
    if inventory and inventory.stock < update_data.quantity:
        raise BadRequestError(detail="Stock insuficiente para la cantidad solicitada")

    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(db: Session, user_id: int, cart_item_id: int) -> None:
    """Remove a single item from the cart."""
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if not cart_item:
        raise NotFoundError(detail=f"Item del carrito con id {cart_item_id} no encontrado")

    db.delete(cart_item)
    db.commit()


def clear_cart(db: Session, user_id: int) -> None:
    """Remove all items from the user's cart."""
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
