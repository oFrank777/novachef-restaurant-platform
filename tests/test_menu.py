"""
MENU PRUEBAS DEL MÓDULO
=================
EP, BVA, edge cases, and attack tests for menu CRUD operations.
"""
import pytest
from tests.conftest import _cabeceras_auth


class TestMenuEP:
    def test_crear_articulo_menu_valid(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "Margherita", "price": 10.50, "category": "Pizza",
            "description": "Classic pizza",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 201
        assert respuesta.json()["name"] == "Margherita"

    def test_crear_sin_autenticacion(self, cliente_api):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "Burger", "price": 8.00, "category": "Burgers",
        })
        assert respuesta.status_code == 401

    def test_crear_non_admin(self, cliente_api, token_cliente):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "Salad", "price": 7.00, "category": "Salads",
        }, headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 403

    def test_obtener_all_articulo_menus(self, cliente_api, articulo_menu_ejemplo):
        respuesta = cliente_api.get("/api/menu/")
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1

    def test_obtener_single_articulo_menu(self, cliente_api, articulo_menu_ejemplo):
        respuesta = cliente_api.get(f"/api/menu/{articulo_menu_ejemplo['id']}")
        assert respuesta.status_code == 200
        assert respuesta.json()["name"] == articulo_menu_ejemplo["name"]

    def test_actualizar_articulo_menu(self, cliente_api, token_admin, articulo_menu_ejemplo):
        respuesta = cliente_api.put(f"/api/menu/{articulo_menu_ejemplo['id']}", json={
            "price": 15.99,
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 200

    def test_delete_articulo_menu(self, cliente_api, token_admin, articulo_menu_ejemplo):
        respuesta = cliente_api.delete(f"/api/menu/{articulo_menu_ejemplo['id']}",
                             headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 204


class TestMenuBVA:
    @pytest.mark.parametrize("longitud,esperado", [
        (2, 422), (3, 201), (4, 201), (49, 201), (50, 201), (51, 422),
    ])
    def test_name_longitud(self, cliente_api, token_admin, longitud, esperado):
        name = "A" * longitud
        respuesta = cliente_api.post("/api/menu/", json={
            "name": name, "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"len={longitud} got {resp.status_code}"

    @pytest.mark.parametrize("price,esperado", [
        (0.00, 422), (0.01, 201), (0.02, 201),
        (999.98, 201), (999.99, 201), (1000.00, 422),
    ])
    def test_price_limites(self, cliente_api, token_admin, price, esperado):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": f"Item_{price}", "price": price, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == esperado, f"price={price} got {resp.status_code}"


class TestMenuCasosExtremos:
    def test_empty_name(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "", "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422

    def test_negative_price(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "NegPrice", "price": -1.0, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422

    def test_price_infinity(self, cliente_api, token_admin):
        
        
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "InfPrice", "price": 1e308, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code == 422

    def test_obtener_nonexistent(self, cliente_api):
        respuesta = cliente_api.get("/api/menu/99999")
        assert respuesta.status_code == 404


class TestMenuFiltersAndPagination:
    def _setup_articulos(self, cliente_api, token_admin):
        for i in range(15):
            cat = "Pizza" if i % 2 == 0 else "Burger"
            avail = True if i % 3 != 0 else False
            cliente_api.post("/api/menu/", json={
                "name": f"Item {i}", "price": 10.0 + i, "category": cat, "is_available": avail
            }, headers=_cabeceras_auth(token_admin))
            
    def test_pagination_limit_skip(self, cliente_api, token_admin):
        self._setup_articulos(cliente_api, token_admin)
        resp1 = cliente_api.get("/api/menu/?skip=0&limit=5")
        assert len(resp1.json()) == 5
        respuesta2 = cliente_api.get("/api/menu/?skip=5&limit=5")
        assert len(respuesta2.json()) == 5
        assert resp1.json()[0]["id"] != respuesta2.json()[0]["id"]

    def test_filter_category(self, cliente_api, token_admin):
        self._setup_articulos(cliente_api, token_admin)
        respuesta = cliente_api.get("/api/menu/?category=Pizza")
        assert respuesta.status_code == 200
        assert all(i["category"] == "Pizza" for i in respuesta.json())

    def test_filter_availability(self, cliente_api, token_admin):
        self._setup_articulos(cliente_api, token_admin)
        respuesta = cliente_api.get("/api/menu/?available_only=true")
        assert respuesta.status_code == 200
        assert all(i["is_available"] is True for i in respuesta.json())

    def test_filter_search_term(self, cliente_api, token_admin):
        cliente_api.post("/api/menu/", json={
            "name": "UniquePasta", "price": 12.0, "category": "Pasta"
        }, headers=_cabeceras_auth(token_admin))
        respuesta = cliente_api.get("/api/menu/?search=Unique")
        assert respuesta.status_code == 200
        assert len(respuesta.json()) >= 1
        assert "Unique" in respuesta.json()[0]["name"]

class TestMenuAttacks:
    def test_sql_injection_name(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "'; DROP TABLE menu_articulos; --",
            "price": 10.00, "category": "Prueba",
        }, headers=_cabeceras_auth(token_admin))
        
        assert respuesta.status_code in (201, 422)

    def test_xss_description(self, cliente_api, token_admin):
        respuesta = cliente_api.post("/api/menu/", json={
            "name": "XSSTest", "price": 10.00, "category": "Prueba",
            "description": "<script>alert('xss')</script>",
        }, headers=_cabeceras_auth(token_admin))
        assert respuesta.status_code in (201, 422)
