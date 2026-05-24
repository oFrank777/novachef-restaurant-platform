"""
OWASP-oriented security regression tests.
"""
import pytest
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


class TestBrokenAccessControl:
    def test_registro_publico_fuerza_rol_cliente(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "hacker_admin_x",
            "first_name": "Hack",
            "last_name": "Admin",
            "email": "hackadmin@example.com",
            "password": "HackPass123",
            "role": "admin",
        })
        assert respuesta.status_code == 201
        assert respuesta.json()["role"] == "cliente"

    def test_cliente_no_accede_pedido_ajeno(self, cliente_api, token_cliente, pedido_ejemplo):
        token_otro = _registrar_e_iniciar_sesion(cliente_api, "otro_cli_sec", "cliente")
        respuesta = cliente_api.get(
            f"/api/orders/{pedido_ejemplo['id']}",
            headers=_cabeceras_auth(token_otro),
        )
        assert respuesta.status_code == 403

    def test_cajero_ve_todos_los_pedidos(self, cliente_api, token_cajero, pedido_ejemplo):
        respuesta = cliente_api.get("/api/orders/", headers=_cabeceras_auth(token_cajero))
        assert respuesta.status_code == 200
        ids = [o["id"] for o in respuesta.json()]
        assert pedido_ejemplo["id"] in ids


class TestInjectionAndValidation:
    def test_cancelar_usa_cancelado_no_cancelled(self, cliente_api, token_admin, pedido_ejemplo):
        respuesta = cliente_api.patch(
            f"/api/orders/{pedido_ejemplo['id']}/status",
            json={"status": "CANCELLED"},
            headers=_cabeceras_auth(token_admin),
        )
        assert respuesta.status_code == 422

    def test_estado_pedido_query_invalido(self, cliente_api, token_admin):
        respuesta = cliente_api.get(
            "/api/orders/?status=DROP TABLE",
            headers=_cabeceras_auth(token_admin),
        )
        assert respuesta.status_code == 400

    @pytest.mark.parametrize("payload", [
        "' OR 1=1 --",
        "<script>alert(1)</script>",
        "A" * 5000,
    ])
    def test_registro_rechaza_payloads(self, cliente_api, payload):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": payload if len(payload) <= 30 else "x" * 30,
            "first_name": payload,
            "last_name": "Test",
            "email": "bad@example.com",
            "password": "ValidPass1",
            "role": "cliente",
        })
        assert respuesta.status_code in (400, 422)


class TestAuthenticationFailures:
    def test_token_invalido_rechazado(self, cliente_api):
        respuesta = cliente_api.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token.invalido"},
        )
        assert respuesta.status_code == 401

    def test_login_credenciales_invalidas(self, cliente_api):
        respuesta = cliente_api.post(
            "/api/auth/login",
            data={"username": "noexiste", "password": "WrongPass1"},
        )
        assert respuesta.status_code == 401


class TestIdempotency:
    def test_idempotency_key_duplicada(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        key = "test-idem-key-001"
        headers = {**_cabeceras_auth(token_cliente), "Idempotency-Key": key}
        body = {"delivery_address": "Calle Segura 123"}
        r1 = cliente_api.post("/api/orders/", json=body, headers=headers)
        r2 = cliente_api.post("/api/orders/", json=body, headers=headers)
        assert r1.status_code == 201
        assert r2.status_code == 409


class TestPaymentAVL:
    def test_pago_efectivo_sin_tarjeta(self, cliente_api, token_cliente, pedido_ejemplo):
        respuesta = cliente_api.post(
            "/api/payments/",
            json={
                "order_id": pedido_ejemplo["id"],
                "amount": pedido_ejemplo["total_amount"],
                "payment_method": "cash",
            },
            headers=_cabeceras_auth(token_cliente),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["card_last_four"] == "CASH"
