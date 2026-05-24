"""
DELIVERY PRUEBAS DEL MÓDULO
=====================
Pruebas EP, BVA y casos extremos para delivery management.
"""
import pytest
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


class TestEntregaEP:
    def _configurar_pedido(self, cliente_api, token_admin):
        articulo = cliente_api.post("/api/menu/", json={
            "name": "Del Pizza", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, f"deluser_{articulo['id']}", "cliente")
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion Entrega 123",
        }, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        return pedido

    def test_crear_entrega(self, cliente_api, token_admin):
        pedido = self._configurar_pedido(cliente_api, token_admin)
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": 5.0, "address": "Direccion de Entrega de Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 201
        assert respuesta.json()["delivery_cost"] > 0

    def test_obtener_entrega(self, cliente_api, token_admin):
        pedido = self._configurar_pedido(cliente_api, token_admin)
        ent = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": 3.0, "address": "Dir para prueba obtener",
        }, headers=_cabeceras_auth(token_admin)).json()
        respuesta = cliente_api.get(f"/api/delivery/{ent['id']}",
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200

    def test_obtener_entrega_by_pedido(self, cliente_api, token_admin):
        pedido = self._configurar_pedido(cliente_api, token_admin)
        cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": 2.0, "address": "Dir por prueba pedido",
        }, headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.get(f"/api/delivery/order/{pedido['id']}",
                          headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200

    def test_crear_entrega_sin_autenticacion(self, cliente_api):
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": 1, "distance_km": 5.0, "address": "Direccion sin autorizacion",
        })
        assert respuesta.status_code == 401


class TestEntregaBVA:
    def _setup(self, cliente_api, token_admin, suffix):
        articulo = cliente_api.post("/api/menu/", json={
            "name": f"DBva{suffix}", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        safe_suffix = str(suffix).replace('.', '_').replace('-', 'n')
        token = _registrar_e_iniciar_sesion(cliente_api, f"dbva_{safe_suffix}", "cliente")
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion Prueba BVA",
        }, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        return pedido

    @pytest.mark.parametrize("distancia,esperado", [
        (0.4, 422), (0.5, 201), (0.6, 201), (19.9, 201), (20.0, 201), (20.1, 422),
    ])
    def test_distance_limites(self, cliente_api, token_admin, distancia, esperado):
        pedido = self._setup(cliente_api, token_admin, f"d{distancia}")
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": distancia, "address": "BVA Addr Test",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"dist={distancia} got {resp.status_code}"

    @pytest.mark.parametrize("longitud,esperado", [
        (4, 422), (5, 201), (6, 201), (199, 201), (200, 201), (201, 422),
    ])
    def test_address_longitud(self, cliente_api, token_admin, longitud, esperado):
        pedido = self._setup(cliente_api, token_admin, f"a{longitud}")
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": 5.0, "address": "A" * longitud,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"len={longitud} got {resp.status_code}"


class TestEntregaCasosExtremos:
    def test_negative_distance(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": 1, "distance_km": -1.0, "address": "Neg dist test",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422

    def test_inexistente_pedido(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": 99999, "distance_km": 5.0, "address": "Prueba de pedido inexistente",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code in (400, 404)

    def test_cost_calculation(self, cliente_api, token_admin):
        """Verificar costo = tarifa_base(2.0) + distance * rate(1.5)."""
        
        articulo = cliente_api.post("/api/menu/", json={
            "name": "CostCalc", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, "costcalc_user", "cliente")
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Direccion Calculo Costo",
        }, headers=_cabeceras_auth(token)).json()

        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))

        distancia = 10.0
        respuesta = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": distancia, "address": "Cost test addr",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 201
        expected_cost = 2.0 + (distancia * 1.5)
        assert abs(respuesta.json()["delivery_cost"] - expected_cost) < 0.01

    def test_entrega_state_machine(self, cliente_api, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "DelSM", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 50, "min_stock": 5}, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, "delsm_user", "cliente")
        cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={"delivery_address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        
        entrega = cliente_api.post("/api/delivery/", json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token_admin)).json()
        
        respuesta = cliente_api.patch(f"/api/delivery/{entrega['id']}/status", json={"status": "RECOGIDO"}, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200
        
        respuesta = cliente_api.patch(f"/api/delivery/{entrega['id']}/status", json={"status": "ASIGNADO"}, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400
        
        cliente_api.patch(f"/api/delivery/{entrega['id']}/status", json={"status": "EN_TRANSITO"}, headers=_cabeceras_auth(token_admin))
        cliente_api.patch(f"/api/delivery/{entrega['id']}/status", json={"status": "ENTREGADO"}, headers=_cabeceras_auth(token_admin))
        
        respuesta = cliente_api.patch(f"/api/delivery/{entrega['id']}/status", json={"status": "RECOGIDO"}, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400

    def test_assign_non_entrega_role(self, cliente_api, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "DelRole", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 50, "min_stock": 5}, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, "delrole_user", "cliente")
        cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={"delivery_address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        
        token_cajero = _registrar_e_iniciar_sesion(cliente_api, "cajero_drv", "cajero")
        id_cajero = cliente_api.get("/api/auth/me", headers=_cabeceras_auth(token_cajero)).json()["id"]
        
        respuesta = cliente_api.post("/api/delivery/", json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Direccion Prueba 123", "driver_id": id_cajero}, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 400
        
    def test_double_entrega_creation(self, cliente_api, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "DelDouble", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 50, "min_stock": 5}, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, "deldouble_user", "cliente")
        cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={"delivery_address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        
        cliente_api.post("/api/delivery/", json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token_admin))
        respuesta2 = cliente_api.post("/api/delivery/", json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token_admin))
        assert respuesta2.status_code == 400
        
    def test_sql_injection_address(self, cliente_api, token_admin):
        articulo = cliente_api.post("/api/menu/", json={"name": "DelSqli", "price": 10.0, "category": "Prueba"}, headers=_cabeceras_auth(token_admin)).json()
        cliente_api.post("/api/inventory/", json={"menu_item_id": articulo["id"], "stock": 50, "min_stock": 5}, headers=_cabeceras_auth(token_admin))
        token = _registrar_e_iniciar_sesion(cliente_api, "delsqli_user", "cliente")
        cliente_api.post("/api/cart/", json={"menu_item_id": articulo["id"], "quantity": 1}, headers=_cabeceras_auth(token))
        pedido = cliente_api.post("/api/orders/", json={"delivery_address": "Direccion Prueba 123"}, headers=_cabeceras_auth(token)).json()
        cliente_api.patch(f"/api/orders/{pedido['id']}/status", json={"status": "PREPARANDO"}, headers=_cabeceras_auth(token_admin))
        
        respuesta = cliente_api.post("/api/delivery/", json={"order_id": pedido["id"], "distance_km": 5.0, "address": "DROP TABLE users; --"}, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422
