import pytest

from tests.conftest import _cabeceras_auth




menu_name_bva = [(2, 422), (3, 201), (50, 201), (51, 422)]
menu_price_bva = [(-0.01, 422), (0.00, 422), (0.01, 201), (999.99, 201), (1000.00, 422)]
menu_desc_bva = [(0, 201), (500, 201), (501, 422)]

menu_cases = []
for nl, ns in menu_name_bva:
    for pl, ps in menu_price_bva:
        for dl, ds in menu_desc_bva:
            esperado = 422 if 422 in (ns, ps, ds) else 201
            menu_cases.append((nl, pl, dl, esperado))

@pytest.mark.parametrize("name_len, price, desc_len, esperado", menu_cases)
def test_massive_menu_bva(cliente_api, token_admin, name_len, price, desc_len, esperado):
    cuerpo_peticion = {
        "name": "M" * name_len,
        "price": price,
        "category": "Pizza",
        "description": "D" * desc_len
    }
    respuesta = cliente_api.post("/api/menu/", json=cuerpo_peticion, headers=_cabeceras_auth(token_admin))
    assert respuesta.status_code == esperado



cart_qty_bva = [(-1, 422), (0, 422), (1, 201), (99, 201), (100, 422), (9999, 422)]
attacks = ["", " ", "' OR 1=1 --", "<script>alert(1)</script>", "😊" * 100]

cart_cases = []
for q, qs in cart_qty_bva:
    for att in attacks:
        cart_cases.append((q, qs, att))

@pytest.mark.parametrize("qty, esperado, attack", cart_cases)
def test_massive_carrito_bva(cliente_api, token_cliente, articulo_menu_ejemplo, qty, esperado, attack):
    cuerpo_peticion = {
        "menu_item_id": articulo_menu_ejemplo["id"],
        "quantity": qty,
        "notes": attack
    }
    respuesta = cliente_api.post("/api/cart/", json=cuerpo_peticion, headers=_cabeceras_auth(token_cliente))
    assert respuesta.status_code == esperado



dist_bva = [(0.4, 422), (0.5, 201), (20.0, 201), (20.1, 422)]
addr_bva = [(4, 422), (5, 201), (200, 201), (201, 422)]

delivery_cases = [(ent, ds, a, list_as) for ent, ds in dist_bva for a, list_as in addr_bva]

@pytest.mark.parametrize("distancia, ds, addr_len, as_expected", delivery_cases)
def test_massive_entrega_bva(cliente_api, token_admin, pedido_ejemplo, distancia, ds, addr_len, as_expected):
    esperado = 422 if 422 in (ds, as_expected) else 201
    cuerpo_peticion = {
        "order_id": pedido_ejemplo["id"],
        "distance_km": distancia,
        "address": "A" * addr_len
    }
    respuesta = cliente_api.post("/api/delivery/", json=cuerpo_peticion, headers=_cabeceras_auth(token_admin))
    if esperado == 422:
        assert respuesta.status_code == 422
    else:
        
        assert respuesta.status_code in (201, 400, 404, 409)



amt_bva = [(-1, 422), (0.00, 422), (0.01, 201), (5000.00, 201), (5000.01, 422)]
card_bva = ["123", "123456789012345", "1234567890123456", "12345678901234567", "abcdefghabcdefgh"]
cvv_bva = ["12", "123", "1234", "abc"]

payment_cases = []
for amt, ast in amt_bva:
    for c in card_bva:
        for v in cvv_bva:
            payment_cases.append((amt, c, v, ast))

@pytest.mark.parametrize("monto, card, cvv, ast", payment_cases)
def test_massive_payments_bva(cliente_api, token_cliente, pedido_ejemplo, monto, card, cvv, ast):
    cuerpo_peticion = {
        "order_id": pedido_ejemplo["id"],
        "amount": monto,
        "card_number": card,
        "cvv": cvv
    }
    respuesta = cliente_api.post("/api/payments/", json=cuerpo_peticion, headers=_cabeceras_auth(token_cliente))
    if ast == 422:
        assert respuesta.status_code == 422
    else:
        
        assert respuesta.status_code in (201, 400, 404, 409, 422)



stock_bva = [(-1, 422), (0, 200), (9999, 200), (10000, 422)]
min_stock_bva = [(-1, 422), (0, 200), (999, 200), (1000, 422)]

inv_cases = []
for s, ss in stock_bva:
    for m, ms in min_stock_bva:
        esperado = 422 if 422 in (ss, ms) else 200
        inv_cases.append((s, m, esperado))

@pytest.mark.parametrize("stock, min_stock, esperado", inv_cases)
def test_massive_inventory_bva(cliente_api, token_admin, articulo_menu_ejemplo, stock, min_stock, esperado):
    cuerpo_peticion = {
        "stock": stock,
        "min_stock": min_stock
    }
    respuesta = cliente_api.put(f"/api/inventory/{articulo_menu_ejemplo['id']}", json=cuerpo_peticion, headers=_cabeceras_auth(token_admin))
    if esperado == 422:
        assert respuesta.status_code == 422
    else:
        assert respuesta.status_code in (200, 400, 404, 409)
