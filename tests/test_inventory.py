"""
INVENTORY PRUEBAS DEL MÓDULO
======================
Pruebas EP, BVA y casos extremos para inventory management.
"""
import pytest
from tests.conftest import _cabeceras_auth


class TestInventarioEP:
    def test_crear_inventory(self, cliente_api, token_admin, articulo_menu_ejemplo):
        respuesta = cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": 100, "min_stock": 10,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 201

    def test_obtener_all_inventory(self, cliente_api, token_admin, inventario_ejemplo):
        respuesta = cliente_api.get("/api/inventory/", headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1

    def test_actualizar_inventory(self, cliente_api, token_admin, inventario_ejemplo):
        respuesta = cliente_api.put(f"/api/inventory/{inventario_ejemplo['id']}", json={
            "stock": 200,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200

    def test_obtener_low_stock(self, cliente_api, token_admin, articulo_menu_ejemplo):
        
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": 3, "min_stock": 10,
        }, headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.get("/api/inventory/low-stock",
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1


class TestInventarioBVA:
    @pytest.mark.parametrize("stock,esperado", [
        (-1, 422), (0, 201), (1, 201), (9998, 201), (9999, 201), (10000, 422),
    ])
    def test_stock_limites(self, cliente_api, token_admin, articulo_menu_ejemplo, stock, esperado):
        respuesta = cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": stock, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"stock={stock} got {resp.status_code}"

    @pytest.mark.parametrize("min_stock,esperado", [
        (-1, 422), (0, 201), (1, 201), (998, 201), (999, 201), (1000, 422),
    ])
    def test_min_stock_limites(self, cliente_api, token_admin, articulo_menu_ejemplo, min_stock, esperado):
        respuesta = cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": 100, "min_stock": min_stock,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"min_stock={min_stock} got {resp.status_code}"


class TestInventarioCasosExtremos:
    def test_no_admin_access(self, cliente_api, token_cliente):
        respuesta = cliente_api.get("/api/inventory/", headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 403

    def test_inexistente_inventory(self, cliente_api, token_admin):
        respuesta = cliente_api.get("/api/inventory/99999", headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 404

    def test_crear_duplicate_inventory(self, cliente_api, token_admin, articulo_menu_ejemplo):
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": 100, "min_stock": 10,
        }, headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo_menu_ejemplo["id"], "stock": 50, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 409

    def test_crear_inventory_inexistente_articulo_menu(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/inventory/", json={
            "menu_item_id": 99999, "stock": 100, "min_stock": 10,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 404

    def test_actualizar_negative_stock(self, cliente_api, token_admin, inventario_ejemplo):
        respuesta = cliente_api.put(f"/api/inventory/{inventario_ejemplo['id']}", json={
            "stock": -1,
        }, headers=_cabeceras_auth(token_admin))
        
        assert respuesta.status_code == 422

    def test_actualizar_inventory_non_admin(self, cliente_api, token_cliente, inventario_ejemplo):
        respuesta = cliente_api.put(f"/api/inventory/{inventario_ejemplo['id']}", json={
            "stock": 200,
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 403
