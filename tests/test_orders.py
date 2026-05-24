"""
ORDERS PRUEBAS DEL MÓDULO
====================
State machine enforcement, EP, BVA, and flow tests.
"""
import pytest
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


class TestPedidosEP:
    def test_crear_pedido(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        respuesta = cliente_api.post("/api/orders/", json={
            "delivery_address": "123 Main St", "notes": "Ring bell",
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 201
        assert respuesta.json()["status"] == "PENDIENTE"

    def test_crear_pedido_empty_carrito(self, cliente_api, token_cliente):
        respuesta = cliente_api.post("/api/orders/", json={},
                           headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_obtener_pedidos_list(self, cliente_api, token_cliente, pedido_ejemplo):
        respuesta = cliente_api.get("/api/orders/", headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1

    def test_obtener_pedido_detail(self, cliente_api, token_cliente, pedido_ejemplo):
        respuesta = cliente_api.get(f"/api/orders/{pedido_ejemplo['id']}",
                          headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 200

    def test_crear_pedido_sin_autenticacion(self, cliente_api):
        respuesta = cliente_api.post("/api/orders/", json={})
        assert respuesta.status_code == 401






class TestMaquinaEstadosPedido:
    """Test EVERY valid and invalid state transition."""

    def _make_pedido(self, cliente_api, token_admin):
        """Helper: create a menu item, inventory, add to cart as new user, create order."""
        
        articulo = cliente_api.post("/api/menu/", json={
            "name": "SM Pizza", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin)).json()
        
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        
        token = _registrar_e_iniciar_sesion(cliente_api, f"smuser_{articulo['id']}", "cliente")
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion Prueba 123",
        }, headers=_cabeceras_auth(token)).json()
        return pedido

    def test_pending_to_preparing(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PREPARANDO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "PREPARANDO"

    def test_pending_to_cancelled(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "CANCELADO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "CANCELADO"

    def test_preparing_to_ready(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                   json={"status": "PREPARANDO"},
                   headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "LISTO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "LISTO"

    def test_shipped_to_delivered(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        for status in ["PREPARANDO", "LISTO", "RECOGIDO", "ENVIADO"]:
            cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                       json={"status": status},
                       headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "ENTREGADO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "ENTREGADO"

    

    def test_pending_to_delivered_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "ENTREGADO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_pending_to_shipped_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "ENVIADO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_delivered_to_pending_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        for status in ["PREPARANDO", "LISTO", "RECOGIDO", "ENVIADO", "ENTREGADO"]:
            cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                       json={"status": status},
                       headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PENDIENTE"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_cancelled_to_preparing_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                   json={"status": "CANCELADO"},
                   headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PREPARANDO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_preparing_to_pending_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                   json={"status": "PREPARANDO"},
                   headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PENDIENTE"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_delivered_to_cancelled_invalid(self, cliente_api, token_admin):
        pedido = self._make_pedido(cliente_api, token_admin)
        for status in ["PREPARANDO", "LISTO", "RECOGIDO", "ENVIADO", "ENTREGADO"]:
            cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                       json={"status": status},
                       headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "CANCELADO"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400


class TestPedidosBVA:
    @pytest.mark.parametrize("longitud,esperado", [
        (4, 422), (5, 201), (6, 201), (199, 201), (200, 201), (201, 422),
    ])
    def test_entrega_address_longitud(self, cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo, longitud, esperado):
        
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token_cliente))
        respuesta = cliente_api.post("/api/orders/", json={
            "delivery_address": "A" * longitud,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == esperado, f"len={longitud} got {resp.status_code}"


class TestPedidosCasosExtremos:
    def test_actualizar_status_non_admin(self, cliente_api, token_cliente, pedido_ejemplo):
        respuesta = cliente_api.patch(f"/api/orders/{pedido_ejemplo['id']}/status",
                          json={"status": "PREPARANDO"},
                          headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 403

    def test_inexistente_pedido(self, cliente_api, token_admin):
        respuesta = cliente_api.get("/api/orders/99999", headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 404

    def test_pedido_unavailable_articulo_menu(self, cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo, token_admin):
        
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token_cliente))
        
        
        cliente_api.put(f"/api/menu/{articulo_menu_ejemplo['id']}", json={"is_available": False}, headers=_cabeceras_auth(token_admin))
        
        
        respuesta = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion de Prueba",
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_pedido_exceeding_inventory(self, cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo):
        
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 999,
        }, headers=_cabeceras_auth(token_cliente))
        
        respuesta = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion de Prueba",
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_double_pedido_from_same_carrito(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        
        resp1 = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion de Prueba",
        }, headers=_cabeceras_auth(token_cliente))
        assert resp1.status_code == 201
        
        
        respuesta2 = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion de Prueba",
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta2.status_code == 400
        
    def test_cross_user_pedido_access(self, cliente_api, pedido_ejemplo):
        
        token2 = _registrar_e_iniciar_sesion(cliente_api, "other_user", "cliente")
        respuesta = cliente_api.get(f"/api/orders/{pedido_ejemplo['id']}", headers=_cabeceras_auth(token2))
        assert respuesta.status_code == 403

    def test_invalid_status_update(self, cliente_api, token_admin, pedido_ejemplo):
        respuesta = cliente_api.patch(f"/api/orders/{pedido_ejemplo['id']}/status",
                          json={"status": "NOT_A_STATUS"},
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422
