"""
Fixtures de prueba compartidos para la API del Restaurante.
Usa una base de datos SQLite en memoria para que cada prueba inicie limpia.
"""

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool



BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app





TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


from app.config import settings
settings.RATE_LIMIT_PER_MINUTE = 10000
settings.AUTH_RATE_LIMIT_PER_MINUTE = 10000








@pytest.fixture(autouse=True)
def setup_db():
    """Crear todas las tablas antes de cada prueba y eliminarlas después."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def cliente_api():
    """Un TestClient nuevo para cada prueba."""
    return TestClient(app)




def _cabeceras_auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_usuario_en_bd(usuario: str, role: str, password: str = "PruebaClave1") -> None:
    from app.models.user import User
    from app.utils.security import get_password_hash

    db = TestingSessionLocal()
    try:
        if db.query(User).filter(User.username == usuario).first():
            return
        db.add(
            User(
                username=usuario,
                first_name="Prueba",
                last_name="Usuario",
                email=f"{usuario}@test.com",
                hashed_password=get_password_hash(password),
                role=role,
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()


def _registrar_e_iniciar_sesion(cliente_api: TestClient, usuario: str, role: str = "cliente") -> str:
    """Registrar un usuario y devolver el token de acceso."""
    password = "PruebaClave1"
    if role == "cliente":
        cliente_api.post(
            "/api/auth/register",
            json={
                "username": usuario,
                "first_name": "Prueba",
                "last_name": "Usuario",
                "email": f"{usuario}@test.com",
                "password": password,
                "role": "cliente",
            },
        )
    else:
        _crear_usuario_en_bd(usuario, role, password)
    respuesta = cliente_api.post(
        "/api/auth/login",
        data={"username": usuario, "password": password},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


@pytest.fixture
def token_admin(cliente_api):
    return _registrar_e_iniciar_sesion(cliente_api, "usuario_admin", "admin")


@pytest.fixture
def token_cliente(cliente_api):
    return _registrar_e_iniciar_sesion(cliente_api, "usuario_cliente", "cliente")


@pytest.fixture
def token_cajero(cliente_api):
    return _registrar_e_iniciar_sesion(cliente_api, "usuario_cajero", "cajero")


@pytest.fixture
def token_entrega(cliente_api):
    return _registrar_e_iniciar_sesion(cliente_api, "usuario_entrega", "delivery")


@pytest.fixture
def articulo_menu_ejemplo(cliente_api, token_admin):
    """Crear un artículo del menú y devolver sus datos."""
    respuesta = cliente_api.post("/api/menu/", json={
        "name": "Pizza de Prueba",
        "description": "Deliciosa pizza de prueba",
        "price": 12.99,
        "category": "Pizza",
        "is_available": True,
    }, headers=_cabeceras_auth(token_admin))
    return respuesta.json()


@pytest.fixture
def inventario_ejemplo(cliente_api, token_admin, articulo_menu_ejemplo):
    """Crear inventario para el artículo de menú de ejemplo."""
    respuesta = cliente_api.post("/api/inventory/", json={
        "menu_item_id": articulo_menu_ejemplo["id"],
        "stock": 100,
        "min_stock": 10,
    }, headers=_cabeceras_auth(token_admin))
    return respuesta.json()


@pytest.fixture
def articulo_carrito_ejemplo(cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo):
    """Agregar el artículo de menú de ejemplo al carrito del cliente."""
    respuesta = cliente_api.post("/api/cart/", json={
        "menu_item_id": articulo_menu_ejemplo["id"],
        "quantity": 2,
    }, headers=_cabeceras_auth(token_cliente))
    return respuesta.json()


@pytest.fixture
def pedido_ejemplo(cliente_api, token_cliente, articulo_carrito_ejemplo):
    """Crear un pedido a partir del carrito del cliente."""
    respuesta = cliente_api.post("/api/orders/", json={
        "delivery_address": "123 Calle Prueba",
        "notes": "Pedido de prueba",
    }, headers=_cabeceras_auth(token_cliente))
    return respuesta.json()
