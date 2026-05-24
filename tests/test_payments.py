"""
PAYMENTS PRUEBAS DEL MÓDULO
=====================
EP, BVA, edge cases, and attack tests for payment processing.
"""
import pytest
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


def _create_pedido_for_payment(cliente_api, token_admin, suffix):
    """Helper: full setup -> menu item -> inventory -> cart -> order."""
    articulo = cliente_api.post("/api/menu/", json={
        "name": f"PayItem{suffix}", "price": 25.50, "category": "Prueba",
    }, headers=_cabeceras_auth(token_admin)).json()
    cliente_api.post("/api/inventory/", json={
        "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
    }, headers=_cabeceras_auth(token_admin))
    token = _registrar_e_iniciar_sesion(cliente_api, f"payuser_{suffix}", "cliente")
    cliente_api.post("/api/cart/", json={
        "menu_item_id": articulo["id"], "quantity": 1,
    }, headers=_cabeceras_auth(token))
    pedido = cliente_api.post("/api/orders/", json={
        "delivery_address": "Payment Test Addr",
    }, headers=_cabeceras_auth(token)).json()
    return pedido, token


class TestPagosEP:
    def test_process_payment_valid(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "valid")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 201
        assert respuesta.json()["status"] == "COMPLETED"

    def test_pago_card_last_four_only(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "lastfour")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "456",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 201
        assert respuesta.json()["card_last_four"] == "1111"
        assert "card_number" not in respuesta.json()

    def test_obtener_payment(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "getpay")
        pay = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "789",
        }, headers=_cabeceras_auth(token)).json()
        respuesta = cliente_api.get(f"/api/payments/{pay['id']}",
                          headers=_cabeceras_auth(token))
        assert respuesta.status_code == 200

    def test_obtener_payment_by_pedido(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "byorder")
        cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "321",
        }, headers=_cabeceras_auth(token))
        respuesta = cliente_api.get(f"/api/payments/order/{pedido['id']}",
                          headers=_cabeceras_auth(token))
        assert respuesta.status_code == 200

    def test_double_payment_rejected(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "double")
        cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "111",
        }, headers=_cabeceras_auth(token))
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "222",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code in (400, 409)


class TestPagosBVA:
    @pytest.mark.parametrize("monto,esperado", [
        (0.00, 422),      
        (0.01, 400),      
        (5000.01, 422),   
    ])
    def test_amount_limites_invalid(self, cliente_api, token_admin, monto, esperado):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, f"amt{str(monto).replace('.', '_').replace('-', 'n')}")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": monto,
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == esperado, f"amount={monto} got {resp.status_code}"

    def test_amount_matching_pedido_total_succeeds(self, cliente_api, token_admin):
        """When amount matches order total exactly, payment succeeds."""
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "match")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 201

    @pytest.mark.parametrize("card,esperado", [
        ("1" * 15, 422), ("4111111111111111", 201), ("1" * 17, 422),
    ])
    def test_card_number_longitud(self, cliente_api, token_admin, card, esperado):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, f"crd{len(card)}")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": card, "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == esperado, f"card len={len(card)} got {resp.status_code}"

    @pytest.mark.parametrize("cvv,esperado", [
        ("12", 422), ("123", 201), ("1234", 422),
    ])
    def test_cvv_longitud(self, cliente_api, token_admin, cvv, esperado):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, f"cv{cvv}")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": cvv,
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == esperado, f"cvv={cvv} got {resp.status_code}"


class TestPaymentsEdge:
    def test_negative_amount(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "negamt")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": -100,
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_card_non_digits(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "nondigit")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "abcdefghijklmnop", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_cvv_non_digits(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "cvvnd")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "abc",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_card_sql_injection(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "sqlicard")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "' OR 1=1 --1234", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_pago_invalid_method(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "badmeth")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "123", "payment_method": "bitcoin"
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422

    def test_pago_cross_user(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "crossuser")
        token2 = _registrar_e_iniciar_sesion(cliente_api, "other_pay_user", "cliente")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token2))
        assert respuesta.status_code == 403

    def test_pago_inexistente_pedido(self, cliente_api, token_admin):
        token = _registrar_e_iniciar_sesion(cliente_api, "pay_nonexistent", "cliente")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": 99999, "amount": 10.0,
            "card_number": "4111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 404

    def test_luhn_invalid_card(self, cliente_api, token_admin):
        pedido, token = _create_pedido_for_payment(cliente_api, token_admin, "luhn")
        respuesta = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "1111111111111111", "cvv": "123",
        }, headers=_cabeceras_auth(token))
        assert respuesta.status_code == 422
