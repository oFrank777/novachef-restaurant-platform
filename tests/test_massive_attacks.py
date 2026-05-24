import pytest
import math

from tests.conftest import _cabeceras_auth



payloads = [
    "",
    " ",
    "   ",
    "' OR 1=1 --",
    '"; DROP TABLE users; --',
    "admin' --",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "a" * 1000,
    "b" * 5000,
    "c" * 10000, 
    "🍕" * 50, 
]

attack_cases = []
for f in ["username", "password"]:
    for p in payloads:
        attack_cases.append((f, p))

@pytest.mark.parametrize("field, cuerpo_peticion", attack_cases)
def test_massive_auth_attacks(cliente_api, field, cuerpo_peticion):
    data = {
        "username": "ValidUser123",
        "email": "valid@test.com",
        "first_name": "Prueba",
        "last_name": "Usuario",
        "password": "ValidPassword1"
    }
    data[field] = cuerpo_peticion
    respuesta = cliente_api.post("/api/auth/register", json=data)
    assert respuesta.status_code == 422


menu_attack_cases = []
for p in payloads:
    for cat in ["Pizza", "Burgers"]:
        menu_attack_cases.append((p, cat))

@pytest.mark.parametrize("cuerpo_peticion, category", menu_attack_cases)
def test_massive_menu_attacks(cliente_api, token_admin, cuerpo_peticion, category):
    data = {
        "name": cuerpo_peticion,
        "price": 10.50,
        "category": category
    }
    respuesta = cliente_api.post("/api/menu/", json=data, headers=_cabeceras_auth(token_admin))
    assert respuesta.status_code in [201, 422, 400]


def test_double_submit_prevention_payments(cliente_api, token_cliente, pedido_ejemplo):
    data = {
        "order_id": pedido_ejemplo["id"],
        "amount": 50.0,
        "card_number": "1234567890123456",
        "cvv": "123"
    }
    headers = _cabeceras_auth(token_cliente)
    headers["Idempotency-Key"] = "unique-payment-key-1234"
    
    
    r1 = cliente_api.post("/api/payments/", json=data, headers=headers)
    assert r1.status_code in [201, 400, 422]
    
    
    r2 = cliente_api.post("/api/payments/", json=data, headers=headers)
    assert r2.status_code == 409
    assert "Envío duplicado prevenido" in r2.json()["detail"]
