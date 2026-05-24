import logging
from sqlalchemy.orm import Session
from app.models.menu import MenuItem
from app.models.inventory import Inventory
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("restaurante_delivery_api")

SEED_MENU = [
    {"name": "Pizza Pepperoni", "description": "Masa artesanal con pepperoni premium y mozzarella", "price": 32.90, "category": "Pizzas", "is_available": True},
    {"name": "Pizza Hawaiana", "description": "Piña caramelizada, jamón ahumado y queso mozzarella", "price": 34.90, "category": "Pizzas", "is_available": True},
    {"name": "Pizza Margherita", "description": "Tomate San Marzano, mozzarella fresca y albahaca", "price": 29.90, "category": "Pizzas", "is_available": True},
    {"name": "Hamburguesa Clásica", "description": "Carne Angus 200g, lechuga, tomate y queso cheddar", "price": 24.90, "category": "Hamburguesas", "is_available": True},
    {"name": "Hamburguesa BBQ", "description": "Doble carne, bacon crocante, cebolla caramelizada y salsa BBQ", "price": 29.90, "category": "Hamburguesas", "is_available": True},
    {"name": "Hamburguesa Vegana", "description": "Proteína vegetal, aguacate, rúcula y mayonesa vegana", "price": 26.90, "category": "Hamburguesas", "is_available": True},
    {"name": "Pollo Broaster", "description": "Piezas de pollo crujiente con especias secretas (6 piezas)", "price": 28.90, "category": "Platos Fuertes", "is_available": True},
    {"name": "Lomo Saltado", "description": "Lomo fino salteado con cebolla, tomate y papas fritas", "price": 38.90, "category": "Platos Fuertes", "is_available": True},
    {"name": "Lasagna Bolognesa", "description": "Capas de pasta con ragú de carne, bechamel y parmesano", "price": 35.90, "category": "Platos Fuertes", "is_available": True},
    {"name": "Salchipapa Especial", "description": "Papas fritas con salchichas premium, salsas y queso", "price": 18.90, "category": "Platos Fuertes", "is_available": True},
    {"name": "Tacos al Pastor", "description": "3 tacos con carne al pastor, piña, cilantro y cebolla", "price": 22.90, "category": "Platos Fuertes", "is_available": True},
    {"name": "Ceviche Clásico", "description": "Pescado fresco marinado en limón con cebolla y ají", "price": 32.90, "category": "Entradas", "is_available": True},
    {"name": "Ensalada César", "description": "Lechuga romana, crutones, parmesano y aderezo César", "price": 19.90, "category": "Entradas", "is_available": True},
    {"name": "Tequeños de Queso", "description": "8 palitos de masa rellenos de queso con guasacaca", "price": 16.90, "category": "Entradas", "is_available": True},
    {"name": "Alitas BBQ", "description": "10 alitas de pollo bañadas en salsa BBQ ahumada", "price": 24.90, "category": "Entradas", "is_available": True},
    {"name": "Brownie con Helado", "description": "Brownie tibio de chocolate belga con helado de vainilla", "price": 18.90, "category": "Postres", "is_available": True},
    {"name": "Cheesecake de Frutos Rojos", "description": "Tarta de queso cremosa con coulis de frutos rojos", "price": 16.90, "category": "Postres", "is_available": True},
    {"name": "Tres Leches", "description": "Bizcocho bañado en tres leches con canela y crema", "price": 14.90, "category": "Postres", "is_available": True},
    {"name": "Limonada Frozen", "description": "Limonada granizada natural con hierbabuena", "price": 9.90, "category": "Bebidas", "is_available": True},
    {"name": "Jugo de Maracuyá", "description": "Jugo natural de maracuyá con hielo", "price": 8.90, "category": "Bebidas", "is_available": True},
    {"name": "Coca-Cola 500ml", "description": "Bebida gaseosa original bien fría", "price": 5.90, "category": "Bebidas", "is_available": True},
    {"name": "Cerveza Artesanal IPA", "description": "Cerveza artesanal IPA 330ml, notas cítricas", "price": 14.90, "category": "Bebidas", "is_available": True},
    {"name": "Agua Mineral 500ml", "description": "Agua mineral sin gas", "price": 3.90, "category": "Bebidas", "is_available": True},
]


def seed_menu_items(db: Session) -> None:
    existing_users = db.query(User).count()
    if existing_users == 0:
        logger.info("Insertando usuarios por defecto…")
        users = [
            User(username="admin", email="admin@restaurant.com", hashed_password=pwd_context.hash("Admin123"), role="admin"),
            User(username="cliente1", email="cliente1@example.com", hashed_password=pwd_context.hash("Cliente123"), role="cliente"),
            User(username="cajero1", email="cajero1@restaurant.com", hashed_password=pwd_context.hash("Cajero123"), role="cajero"),
            User(username="delivery1", email="delivery1@restaurant.com", hashed_password=pwd_context.hash("Delivery123"), role="delivery")
        ]
        db.add_all(users)
        db.commit()

    existing_count = db.query(MenuItem).count()
    if existing_count > 0:
        return

    logger.info("Insertando %d platillos iniciales en la base de datos…", len(SEED_MENU))
    for item_data in SEED_MENU:
        menu_item = MenuItem(**item_data)
        db.add(menu_item)
    db.flush()

    menu_items = db.query(MenuItem).all()
    for mi in menu_items:
        inv = Inventory(
            menu_item_id=mi.id,
            stock=50,
            min_stock=5,
        )
        db.add(inv)

    db.commit()
    logger.info("Seed completado: %d platillos con inventario inicial.", len(SEED_MENU))
