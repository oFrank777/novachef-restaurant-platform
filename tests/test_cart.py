"""
CART PRUEBAS DEL MÓDULO
=================
Pruebas EP, BVA y casos extremos para shopping cart operations.
"""
import pytest
from tests.conftest import _cabeceras_auth


class TestCarritoEP:
    def test_agregar_to_carrito(self, cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 3,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 201

    def test_obtener_carrito(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        respuesta = cliente_api.get("/api/cart/", headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1

    def test_actualizar_carrito_quantity(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        respuesta = cliente_api.put(f"/api/cart/{articulo_carrito_ejemplo['id']}", json={
            "quantity": 5,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 200

    def test_eliminar_carrito_articulo(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        respuesta = cliente_api.delete(f"/api/cart/{articulo_carrito_ejemplo['id']}",
                             headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 204

    def test_vaciar_carrito(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        respuesta = cliente_api.delete("/api/cart/", headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 204
        cart = cliente_api.get("/api/cart/", headers=_cabeceras_auth(token_cliente))
        assert len(cart.json()) == 0

    def test_agregar_sin_autenticacion(self, cliente_api, articulo_menu_ejemplo):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 1,
        })
        assert respuesta.status_code == 401


class TestCarritoBVA:
    @pytest.mark.parametrize("qty,esperado", [
        (0, 422), (1, 201), (2, 201), (98, 201), (99, 201), (100, 422),
    ])
    def test_quantity_limites(self, cliente_api, token_cliente, articulo_menu_ejemplo, inventario_ejemplo, qty, esperado):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": qty,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == esperado, f"qty={qty} got {resp.status_code}"


class TestCarritoCasosExtremos:
    def test_agregar_inexistente_articulo(self, cliente_api, token_cliente):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": 99999, "quantity": 1,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code in (400, 404)

    def test_agregar_negative_quantity(self, cliente_api, token_cliente, articulo_menu_ejemplo):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": -1,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 422

    def test_agregar_zero_quantity(self, cliente_api, token_cliente, articulo_menu_ejemplo):
        respuesta = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "quantity": 0,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 422

    def test_actualizar_inexistente_carrito_articulo(self, cliente_api, token_cliente):
        respuesta = cliente_api.put("/api/cart/99999", json={"quantity": 1},
                          headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code in (400, 404)

    def test_agregar_unavailable_articulo(self, cliente_api, token_cliente, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "Unavail", "price": 10.0, "category": "Prueba", "is_available": False}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 50, "min_stock": 5}, headers=_cabeceras_auth(token_admin))
        
        respuesta = cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_agregar_exceeding_stock(self, cliente_api, token_cliente, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "LowStock", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 5, "min_stock": 1}, headers=_cabeceras_auth(token_admin))
        
        respuesta = cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 10}, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_actualizar_exceeding_stock(self, cliente_api, token_cliente, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "LowStockUpd", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 5, "min_stock": 1}, headers=_cabeceras_auth(token_admin))
        
        cart_articulo = cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token_cliente)).json()
        
        
        respuesta = cliente_api.put(f"/api/cart/{cart_articulo['id']}", json={"quantity": 10}, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 400

    def test_cross_user_carrito_access(self, cliente_api, token_cliente, articulo_carrito_ejemplo):
        from tests.conftest import _registrar_e_iniciar_sesion
        token2 = _registrar_e_iniciar_sesion(cliente_api, "other_carrito_user", "cliente")
        
        resp_get = cliente_api.get("/api/cart/", headers=_cabeceras_auth(token2))
        assert len(resp_get.json()) == 0
        
        respuesta_act = cliente_api.put(f"/api/cart/{articulo_carrito_ejemplo['id']}", json={"quantity": 5}, headers=_cabeceras_auth(token2))
        assert respuesta_act.status_code in (403, 404)
        
        resp_del = cliente_api.delete(f"/api/cart/{articulo_carrito_ejemplo['id']}", headers=_cabeceras_auth(token2))
        assert resp_del.status_code in (403, 404)
