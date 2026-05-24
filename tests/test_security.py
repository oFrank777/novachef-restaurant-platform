"""
SECURITY TESTS
==============
Attack vector tests: SQL injection, XSS, overflow, and malicious inputs.
"""
import pytest
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


class TestSQLInjection:
    def test_sqli_login_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "' OR 1=1 --", "password": "anything",
        })
        assert respuesta.status_code == 401

    def test_sqli_login_contrasena(self, cliente_api):
        _registrar_e_iniciar_sesion(cliente_api, "sqli_target", "cliente")
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "sqli_target", "password": "' OR 1=1 --",
        })
        assert respuesta.status_code == 401

    def test_sqli_register(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "'; DROP TABLE users; --",
            "first_name": "Prueba", "last_name": "Usuario", "email": "sqli@test.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_sqli_menu_name(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "sqli_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "'; DELETE FROM menu_articulos; --",
            "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token))
        
        assert respuesta.status_code in (201, 422)
        
        if respuesta.status_code == 201:
            items = cliente_api.get("/api/menu/").json()
            assert len(items) >= 1  


class TestXSS:
    def test_xss_in_menu_description(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "xss_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "XSSMenu", "price": 10.00, "category": "Prueba",
            "description": "<script>alert('XSS')</script>",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code in (201, 422)


class TestOverflow:
    def test_overflow_quantity(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "overflow_admin", "admin")
        admin_h = _cabeceras_auth(token)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "OverflowItem", "price": 10.00, "category": "Prueba",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 9999, "min_stock": 5,
        }, headers=admin_h)

        ctok = _registrar_e_iniciar_sesion(cliente_api, "overflow_client", "cliente")
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 999999,
        }, headers=_cabeceras_auth(ctok))
        assert respuesta.status_code == 422

    def test_negative_price(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "negprice_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "NegPriceItem", "price": -999.99, "category": "Prueba",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422


class TestMalformedTokens:
    def test_invalid_jwt(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me", headers=_cabeceras_auth("not-a-token"))
        assert respuesta.status_code == 401

    def test_empty_bearer(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me", headers={"Authorization": "Bearer "})
        assert respuesta.status_code == 401

    def test_no_bearer_prefix(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me", headers={"Authorization": "notbearer xyz"})
        assert respuesta.status_code == 401


class TestCadenasLargas:
    @pytest.mark.parametrize("field,value,endpoint", [
        ("username", "a" * 10000, "/api/auth/register"),
        ("password", "A1a" + "x" * 9997, "/api/auth/register"),
    ])
    def test_very_long_string_inputs(self, cliente_api, field, value, endpoint):
        data = {"username": "longtest", "first_name": "Prueba", "last_name": "Usuario", "email": "long@t.com", "password": "FuerteP1"}
        data[field] = value
        respuesta = cliente_api.post(endpoint, json=data)
        assert respuesta.status_code == 422

    def test_long_menu_name(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "longname_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "A" * 10000, "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_long_entrega_address(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "longaddr_admin", "admin")
        h = _cabeceras_auth(token)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "LongAddr", "price": 10.00, "category": "Prueba",
        }, headers=h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=h)
        ctok = _registrar_e_iniciar_sesion(cliente_api, "longaddr_client", "cliente")
        ch = _cabeceras_auth(ctok)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=ch)
        respuesta = cliente_api.post("/api/orders/", json={
            "delivery_address": "A" * 10000,
        }, headers=ch)
        assert respuesta.status_code == 422

    def test_union_sql_injection(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "union_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "' UNION SELECT 1,2,3 --", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code in (201, 422)

    def test_null_byte_injection(self, cliente_api):
        token = _registrar_e_iniciar_sesion(cliente_api, "null_admin", "admin")
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "Null\x00Byte", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code in (201, 422)
