"""
PRUEBAS DE INTEGRACIÓN
=================
End-to-end flow tests covering complete user journeys through the system.
"""
from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


class TestFlujoCompletoPedido:
    def test_registrar_login_browse_carrito_pedido(self, cliente_api):
        """Complete flow: register → login → browse menu → add to cart → order."""
        
        r = cliente_api.post("/api/auth/register", json={
            "username": "flow_user", "first_name": "Prueba", "last_name": "Usuario", "email": "flow@test.com",
            "password": "FlowPass1", "role": "cliente",
        })
        assert r.status_code == 201

        
        r = cliente_api.post("/api/auth/login", data={
            "username": "flow_user", "password": "FlowPass1",
        })
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = _cabeceras_auth(token)

        
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "flow_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "Flow Burger", "price": 15.00, "category": "Burgers",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h)

        
        r = cliente_api.get("/api/menu/")
        assert r.status_code == 200
        assert any(i["name"] == "Flow Burger" for i in r.json())

        
        r = cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 3,
        }, headers=headers)
        assert r.status_code == 201

        
        r = cliente_api.post("/api/orders/", json={
            "delivery_address": "123 Flow Street",
        }, headers=headers)
        assert r.status_code == 201
        assert r.json()["status"] == "PENDIENTE"
        assert r.json()["total_amount"] == 45.00  

    def test_flujo_completo_payment_flow(self, cliente_api):
        """Flow: … → order → payment."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "pay_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "PayFlow Pizza", "price": 20.00, "category": "Pizza",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h)

        token = _registrar_e_iniciar_sesion(cliente_api, "payflow_user", "cliente")
        h = _cabeceras_auth(token)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 2,
        }, headers=h)
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Pay Flow Street 456",
        }, headers=h).json()

        r = cliente_api.post("/api/payments/", json={
            "order_id": pedido["id"], "amount": pedido["total_amount"],
            "card_number": "4111111111111111", "cvv": "999",
        }, headers=h)
        assert r.status_code == 201
        assert r.json()["status"] == "COMPLETED"

    def test_flujo_completo_entrega_flow(self, cliente_api):
        """Flow: … → order → delivery → status updates."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "del_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "DelFlow Sushi", "price": 30.00, "category": "Sushi",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h)

        token = _registrar_e_iniciar_sesion(cliente_api, "delflow_user", "cliente")
        h = _cabeceras_auth(token)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=h)
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "Del Flow Rd 789",
        }, headers=h).json()

        
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                   json={"status": "PREPARANDO"}, headers=admin_h)

        ent = cliente_api.post("/api/delivery/", json={
            "order_id": pedido["id"], "distance_km": 8.0, "address": "Del Flow Rd 789",
        }, headers=admin_h).json()
        assert ent["delivery_cost"] == 2.0 + 8.0 * 1.5  

    def test_pedido_state_machine_full_flow(self, cliente_api):
        """PENDIENTE → PREPARANDO → ENVIADO → ENTREGADO."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "sm_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "SM Flow Item", "price": 12.00, "category": "Prueba",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h)

        token = _registrar_e_iniciar_sesion(cliente_api, "smflow_user", "cliente")
        h = _cabeceras_auth(token)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 1,
        }, headers=h)
        pedido = cliente_api.post("/api/orders/", json={
            "delivery_address": "SM Flow Street",
        }, headers=h).json()

        for status in ["PREPARANDO", "LISTO", "RECOGIDO", "ENVIADO", "ENTREGADO"]:
            r = cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                           json={"status": status}, headers=admin_h)
            assert r.status_code == 200
            assert r.json()["status"] == status

    def test_inventario_deduction_on_pedido(self, cliente_api):
        """Stock should decrease when an order is placed."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "inv_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "InvDeduct", "price": 5.00, "category": "Prueba",
        }, headers=admin_h).json()
        inv = cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h).json()

        token = _registrar_e_iniciar_sesion(cliente_api, "invdeduct_user", "cliente")
        h = _cabeceras_auth(token)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 10,
        }, headers=h)
        cliente_api.post("/api/orders/", json={}, headers=h)

        updated_inv = cliente_api.get(f"/api/inventory/{inv['id']}",
                                 headers=admin_h).json()
        assert updated_inv["stock"] == 40  

    def test_carrito_clears_after_pedido(self, cliente_api):
        """Cart should be empty after placing an order."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "clrcart_admin", "admin")
        admin_h = _cabeceras_auth(admin_tok)
        articulo = cliente_api.post("/api/menu/", json={
            "name": "ClearCart", "price": 5.00, "category": "Prueba",
        }, headers=admin_h).json()
        cliente_api.post("/api/inventory/", json={
            "menu_item_id": articulo["id"], "stock": 50, "min_stock": 5,
        }, headers=admin_h)

        token = _registrar_e_iniciar_sesion(cliente_api, "clrcart_user", "cliente")
        h = _cabeceras_auth(token)
        cliente_api.post("/api/cart/", json={
            "menu_item_id": articulo["id"], "quantity": 2,
        }, headers=h)
        cliente_api.post("/api/orders/", json={}, headers=h)

        cart = cliente_api.get("/api/cart/", headers=h).json()
        assert len(cart) == 0

    def test_admin_menu_management(self, cliente_api):
        """Admin creates, updates, and deletes a menu item."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "mgmt_admin", "admin")
        h = _cabeceras_auth(admin_tok)

        articulo = cliente_api.post("/api/menu/", json={
            "name": "MgmtItem", "price": 10.00, "category": "Prueba",
        }, headers=h).json()
        assert articulo["name"] == "MgmtItem"

        r = cliente_api.put(f"/api/menu/{articulo['id']}", json={
            "name": "UpdatedMgmt", "price": 15.00,
        }, headers=h)
        assert r.status_code == 200

        r = cliente_api.delete(f"/api/menu/{articulo['id']}", headers=h)
        assert r.status_code == 204

        r = cliente_api.get(f"/api/menu/{articulo['id']}")
        assert r.status_code == 404

    def test_role_based_access(self, cliente_api):
        """Verify admin routes are blocked for clients."""
        admin_tok = _registrar_e_iniciar_sesion(cliente_api, "rbac_admin", "admin")
        client_tok = _registrar_e_iniciar_sesion(cliente_api, "rbac_client", "cliente")

        
        r = cliente_api.post("/api/menu/", json={
            "name": "RBAC", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(client_tok))
        assert r.status_code == 403

        
        r = cliente_api.get("/api/inventory/", headers=_cabeceras_auth(client_tok))
        assert r.status_code == 403

        
        r = cliente_api.get("/api/reports/sales", headers=_cabeceras_auth(client_tok))
        assert r.status_code == 403

        
        cliente_api.post("/api/menu/", json={
            "name": "RBAC OK", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(admin_tok))
        r = cliente_api.get("/api/inventory/", headers=_cabeceras_auth(admin_tok))
        assert r.status_code == 200
