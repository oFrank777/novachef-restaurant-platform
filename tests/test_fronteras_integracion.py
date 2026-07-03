"""
=====================================================================================
 PRÁCTICA 08 — PRUEBAS DE INTEGRACIÓN (EJERCICIO PROPUESTO 2)
 Proyecto Final: NovaChef — Sistema SaaS de Restaurante + Delivery
 Herramienta: pytest + FastAPI TestClient (equivalente Python de Supertest/Requests)
=====================================================================================

TAREA DE ANÁLISIS DE ERRORES (Inyección de Fallas de Interfaz)
--------------------------------------------------------------
Esta suite NO prueba caminos felices (eso lo cubre test_integration.py). Aquí atacamos
deliberadamente las FRONTERAS entre subsistemas para exponer defectos de interfaz,
siguiendo el Modelo en V (nivel de Integración "en pequeña").

FRONTERAS MAPEADAS (Subsistema A entrega control/datos a Subsistema B):
    F1  Carrito      -> Pedido        (POST /api/orders/  consume CartItem)
    F2  Pedido       -> Inventario    (create_order descuenta stock)
    F3  Pedido       -> Pago          (POST /api/payments/ valida monto vs total)
    F4  Pedido       -> Delivery      (POST /api/delivery/ + máquina de estados)
    F5  Auth/Roles   -> Operaciones   (JWT + require_role en cada endpoint)

CATEGORÍAS DE INYECCIÓN (la guía pide 3; entregamos 3 categorías x múltiples casos):
    [SIN]  Sintáctico  -> campos faltantes o tipos de datos erróneos      -> 422/400
    [SEM]  Semántico   -> valores legales pero fuera de lógica de negocio -> 400/403
    [RES]  Resiliencia -> latencia alta / fallo del subsistema B          -> no colapsar

Cada caso lleva un ID (p.ej. SIN-01) que enlaza con el Reporte de Incidente en
    entregables_ejercicio2/02_reportes_incidentes.md
"""

import time
from unittest.mock import patch

from tests.conftest import _cabeceras_auth, _registrar_e_iniciar_sesion


# ---------------------------------------------------------------------------
# Helpers de preparación de estado (reutilizados por varias fronteras)
# ---------------------------------------------------------------------------
def _preparar_producto_con_stock(cliente_api, nombre="Producto Frontera", precio=10.0, stock=50):
    """Crea admin + producto de menú + inventario. Devuelve (admin_headers, articulo)."""
    admin_tok = _registrar_e_iniciar_sesion(cliente_api, f"admin_{nombre}".replace(" ", "_"), "admin")
    admin_h = _cabeceras_auth(admin_tok)
    articulo = cliente_api.post(
        "/api/menu/",
        json={"name": nombre, "price": precio, "category": "Prueba"},
        headers=admin_h,
    ).json()
    cliente_api.post(
        "/api/inventory/",
        json={"menu_item_id": articulo["id"], "stock": stock, "min_stock": 5},
        headers=admin_h,
    )
    return admin_h, articulo


def _cliente_con_carrito(cliente_api, articulo, usuario="cli_frontera", cantidad=2):
    """Registra un cliente y le agrega un artículo al carrito. Devuelve headers del cliente."""
    tok = _registrar_e_iniciar_sesion(cliente_api, usuario, "cliente")
    h = _cabeceras_auth(tok)
    cliente_api.post(
        "/api/cart/",
        json={"menu_item_id": articulo["id"], "quantity": cantidad},
        headers=h,
    )
    return h


def _crear_pedido_domicilio(cliente_api, articulo, usuario="cli_pedido", cantidad=2,
                            direccion="Av. Siempre Viva 742"):
    """Flujo mínimo Carrito->Pedido. Devuelve (headers_cliente, pedido_json)."""
    h = _cliente_con_carrito(cliente_api, articulo, usuario=usuario, cantidad=cantidad)
    pedido = cliente_api.post(
        "/api/orders/", json={"delivery_address": direccion}, headers=h
    ).json()
    return h, pedido


# ===========================================================================
#  FRONTERA F1: CARRITO -> PEDIDO
# ===========================================================================
class TestF1_CarritoPedido:
    """El handoff ocurre en POST /api/orders/: el subsistema Pedido lee los
    CartItem del subsistema Carrito y construye el Order."""

    # --- [SIN] Sintáctico -------------------------------------------------
    def test_SIN01_pedido_con_tipo_de_dato_erroneo_en_notes(self, cliente_api):
        """SIN-01 | Enviar 'notes' como objeto JSON en vez de string.
        Esperado: 422 (contrato de tipo violado, no debe llegar a la BD)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SIN01")
        h = _cliente_con_carrito(cliente_api, articulo, usuario="sin01_user")
        r = cliente_api.post(
            "/api/orders/",
            json={"delivery_address": "Calle Real 123", "notes": {"malicioso": True}},
            headers=h,
        )
        assert r.status_code == 422, r.text

    def test_SIN02_pedido_con_direccion_bajo_longitud_minima(self, cliente_api):
        """SIN-02 | delivery_address de 2 caracteres (< 5 exigidos).
        Esperado: 422 por validación de longitud del contrato."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SIN02")
        h = _cliente_con_carrito(cliente_api, articulo, usuario="sin02_user")
        r = cliente_api.post(
            "/api/orders/", json={"delivery_address": "ab"}, headers=h
        )
        assert r.status_code == 422, r.text

    # --- [SEM] Semántico --------------------------------------------------
    def test_SEM01_pedido_desde_carrito_vacio(self, cliente_api):
        """SEM-01 | Crear pedido sin nada en el carrito (dato legal pero ilógico).
        Esperado: 400 'El carrito está vacío'."""
        tok = _registrar_e_iniciar_sesion(cliente_api, "sem01_user", "cliente")
        r = cliente_api.post(
            "/api/orders/",
            json={"delivery_address": "Calle Vacia 000"},
            headers=_cabeceras_auth(tok),
        )
        assert r.status_code == 400, r.text
        assert "carrito" in r.json()["detail"].lower()

    def test_SEM02_pedido_excede_monto_maximo(self, cliente_api):
        """SEM-02 | Carrito cuyo total supera el máximo permitido ($5000).
        99 uds x $99 = $9801. Esperado: 400 (regla de negocio de frontera)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM02", precio=99.0, stock=200)
        h = _cliente_con_carrito(cliente_api, articulo, usuario="sem02_user", cantidad=99)
        r = cliente_api.post(
            "/api/orders/", json={"delivery_address": "Calle Cara 999"}, headers=h
        )
        assert r.status_code == 400, r.text
        assert "máximo" in r.json()["detail"].lower() or "excede" in r.json()["detail"].lower()


# ===========================================================================
#  FRONTERA F2: PEDIDO -> INVENTARIO
# ===========================================================================
class TestF2_PedidoInventario:
    """El handoff ocurre dentro de create_order: descuenta stock del subsistema
    Inventario y valida disponibilidad."""

    def test_SEM03_stock_insuficiente_bloqueado_en_frontera(self, cliente_api):
        """SEM-03 | Pedir 30 uds cuando solo hay 5 en stock.
        HALLAZGO (defensa en profundidad): la validación de stock se dispara en la
        PRIMERA frontera (Carrito->Inventario, add_to_cart) devolviendo 400 al añadir,
        y existe un guard REDUNDANTE en create_order (Pedido->Inventario) como respaldo.
        Esperado: el POST /api/cart/ ya rechaza con 400 'Stock insuficiente'."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM03", stock=5)
        tok = _registrar_e_iniciar_sesion(cliente_api, "sem03_user", "cliente")
        h = _cabeceras_auth(tok)
        r_cart = cliente_api.post(
            "/api/cart/",
            json={"menu_item_id": articulo["id"], "quantity": 30},
            headers=h,
        )
        assert r_cart.status_code == 400, r_cart.text
        assert "stock" in r_cart.json()["detail"].lower()

        # El respaldo en la frontera Pedido->Inventario: sin carrito válido no hay pedido.
        r_order = cliente_api.post(
            "/api/orders/", json={"delivery_address": "Calle Stock 111"}, headers=h
        )
        assert r_order.status_code == 400, r_order.text

    def test_SEM04_consistencia_descuento_stock(self, cliente_api):
        """SEM-04 | Verificar que el stock se descuenta EXACTAMENTE lo pedido
        (integridad de datos cruzada Pedido<->Inventario)."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SEM04", stock=50)
        inv = cliente_api.get("/api/inventory/", headers=admin_h).json()
        inv_id = next(i["id"] for i in inv if i["menu_item_id"] == articulo["id"])

        h = _cliente_con_carrito(cliente_api, articulo, usuario="sem04_user", cantidad=8)
        cliente_api.post("/api/orders/", json={"delivery_address": "Calle Int 222"}, headers=h)

        inv_final = cliente_api.get(f"/api/inventory/{inv_id}", headers=admin_h).json()
        assert inv_final["stock"] == 42, f"Se esperaba 50-8=42, real={inv_final['stock']}"


# ===========================================================================
#  FRONTERA F3: PEDIDO -> PAGO
# ===========================================================================
class TestF3_PedidoPago:
    """El handoff ocurre en POST /api/payments/: el subsistema Pago lee el Order
    y valida monto, propietario, estado y unicidad."""

    # --- [SIN] Sintáctico -------------------------------------------------
    def test_SIN03_pago_sin_numero_de_tarjeta(self, cliente_api):
        """SIN-03 | payment_method=credit_card pero sin card_number/cvv.
        Esperado: 422 (contrato tarjeta incompleto)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SIN03")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sin03_user")
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": pedido["id"], "amount": pedido["total_amount"]},
            headers=h,
        )
        assert r.status_code == 422, r.text

    def test_SIN04_pago_con_amount_no_numerico(self, cliente_api):
        """SIN-04 | amount enviado como texto no convertible ('mucho dinero').
        Esperado: 422 (tipo inválido en campo numérico)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SIN04")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sin04_user")
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": pedido["id"], "amount": "mucho dinero",
                  "card_number": "4111111111111111", "cvv": "123"},
            headers=h,
        )
        assert r.status_code == 422, r.text

    def test_SIN05_pago_con_tarjeta_de_15_digitos(self, cliente_api):
        """SIN-05 | Número de tarjeta con 15 dígitos (contrato exige 16 + Luhn).
        Esperado: 422."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SIN05")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sin05_user")
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": pedido["id"], "amount": pedido["total_amount"],
                  "card_number": "411111111111111", "cvv": "123"},
            headers=h,
        )
        assert r.status_code == 422, r.text

    # --- [SEM] Semántico --------------------------------------------------
    def test_SEM05_pago_con_monto_distinto_al_total(self, cliente_api):
        """SEM-05 | Pagar $1.00 un pedido de $20.00 (valor legal, lógica inválida).
        Esperado: 400 'monto no coincide'."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM05", precio=20.0)
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sem05_user", cantidad=1)
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": pedido["id"], "amount": 1.00,
                  "card_number": "4111111111111111", "cvv": "123"},
            headers=h,
        )
        assert r.status_code == 400, r.text
        assert "coincide" in r.json()["detail"].lower()

    def test_SEM06_doble_pago_del_mismo_pedido(self, cliente_api):
        """SEM-06 | Pagar dos veces el mismo pedido (idempotencia de negocio).
        Esperado: 1er pago 201, 2do pago 400 'ya existe'."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM06", precio=15.0)
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sem06_user", cantidad=1)
        pago = {"order_id": pedido["id"], "amount": pedido["total_amount"],
                "card_number": "4111111111111111", "cvv": "123"}
        r1 = cliente_api.post("/api/payments/", json=pago, headers=h)
        assert r1.status_code == 201, r1.text
        r2 = cliente_api.post("/api/payments/", json=pago, headers=h)
        assert r2.status_code == 400, r2.text
        assert "ya existe" in r2.json()["detail"].lower()

    def test_SEM07_pago_de_pedido_ajeno(self, cliente_api):
        """SEM-07 | Un cliente intenta pagar el pedido de OTRO cliente.
        Esperado: 403 (aislamiento de propiedad entre subsistemas)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM07", precio=12.0)
        _, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sem07_victima", cantidad=1)

        atacante = _registrar_e_iniciar_sesion(cliente_api, "sem07_atacante", "cliente")
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": pedido["id"], "amount": pedido["total_amount"],
                  "card_number": "4111111111111111", "cvv": "123"},
            headers=_cabeceras_auth(atacante),
        )
        assert r.status_code == 403, r.text

    def test_SEM08_pago_de_pedido_inexistente(self, cliente_api):
        """SEM-08 | order_id que no existe (99999).
        Esperado: 404 (referencia rota entre subsistemas)."""
        tok = _registrar_e_iniciar_sesion(cliente_api, "sem08_user", "cliente")
        r = cliente_api.post(
            "/api/payments/",
            json={"order_id": 99999, "amount": 10.0,
                  "card_number": "4111111111111111", "cvv": "123"},
            headers=_cabeceras_auth(tok),
        )
        assert r.status_code == 404, r.text


# ===========================================================================
#  FRONTERA F4: PEDIDO -> DELIVERY
# ===========================================================================
class TestF4_PedidoDelivery:
    """El handoff ocurre en POST /api/delivery/ y en la máquina de estados del
    pedido. El subsistema Delivery depende del estado y tipo del Order."""

    # --- [SIN] Sintáctico -------------------------------------------------
    def test_SIN06_delivery_con_distancia_fuera_de_rango(self, cliente_api):
        """SIN-06 | distance_km=50 (contrato: máx 20 km).
        Esperado: 422."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SIN06")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sin06_user")
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PREPARANDO"}, headers=admin_h)
        r = cliente_api.post(
            "/api/delivery/",
            json={"order_id": pedido["id"], "distance_km": 50.0, "address": "Calle Lejos 500"},
            headers=admin_h,
        )
        assert r.status_code == 422, r.text

    def test_SIN07_delivery_sin_campo_address(self, cliente_api):
        """SIN-07 | Falta el campo obligatorio 'address'.
        Esperado: 422 (campo requerido ausente)."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SIN07")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sin07_user")
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PREPARANDO"}, headers=admin_h)
        r = cliente_api.post(
            "/api/delivery/",
            json={"order_id": pedido["id"], "distance_km": 5.0},
            headers=admin_h,
        )
        assert r.status_code == 422, r.text

    # --- [SEM] Semántico --------------------------------------------------
    def test_SEM09_delivery_para_pedido_pendiente(self, cliente_api):
        """SEM-09 | Crear entrega para un pedido aún en PENDIENTE (fuera de lógica:
        no se despacha lo que no se ha preparado).
        Esperado: 400."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SEM09")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sem09_user")
        r = cliente_api.post(
            "/api/delivery/",
            json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Calle Pend 123"},
            headers=admin_h,
        )
        assert r.status_code == 400, r.text

    def test_SEM10_delivery_para_pedido_de_recojo_en_local(self, cliente_api):
        """SEM-10 | Pedido marcado 'recojo en local' no admite delivery.
        Esperado: 400 (incoherencia de tipo de pedido)."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SEM10")
        h, pedido = _crear_pedido_domicilio(
            cliente_api, articulo, usuario="sem10_user", direccion="recojo en local"
        )
        cliente_api.patch(f"/api/orders/{pedido['id']}/status",
                          json={"status": "PREPARANDO"}, headers=admin_h)
        r = cliente_api.post(
            "/api/delivery/",
            json={"order_id": pedido["id"], "distance_km": 5.0, "address": "Calle Local 123"},
            headers=admin_h,
        )
        assert r.status_code == 400, r.text

    def test_SEM11_transicion_de_estado_ilegal(self, cliente_api):
        """SEM-11 | Saltar de PENDIENTE directo a ENTREGADO (viola máquina de estados).
        Esperado: 400 'Transición no permitida'."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "SEM11")
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="sem11_user")
        r = cliente_api.patch(
            f"/api/orders/{pedido['id']}/status",
            json={"status": "ENTREGADO"}, headers=admin_h,
        )
        assert r.status_code == 400, r.text
        assert "transici" in r.json()["detail"].lower()


# ===========================================================================
#  FRONTERA F5: AUTH / ROLES -> OPERACIONES
# ===========================================================================
class TestF5_AuthRoles:
    """El handoff de seguridad: cada endpoint delega en get_current_user /
    require_role antes de ceder control al subsistema de negocio."""

    def test_SEM12_cliente_no_puede_crear_inventario(self, cliente_api):
        """SEM-12 | Rol 'cliente' invoca operación de admin.
        Esperado: 403 (frontera de autorización)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "SEM12")
        tok = _registrar_e_iniciar_sesion(cliente_api, "sem12_user", "cliente")
        r = cliente_api.post(
            "/api/inventory/",
            json={"menu_item_id": articulo["id"], "stock": 10, "min_stock": 2},
            headers=_cabeceras_auth(tok),
        )
        assert r.status_code == 403, r.text

    def test_SIN08_token_malformado(self, cliente_api):
        """SIN-08 | Authorization con token basura.
        Esperado: 401 (credencial sintácticamente inválida)."""
        r = cliente_api.get(
            "/api/orders/", headers={"Authorization": "Bearer no-es-un-jwt-valido"}
        )
        assert r.status_code == 401, r.text

    def test_SEM13_acceso_sin_token(self, cliente_api):
        """SEM-13 | Operar sin cabecera Authorization.
        Esperado: 401/403 (frontera cerrada por defecto)."""
        r = cliente_api.post(
            "/api/orders/", json={"delivery_address": "Calle Sin Token 1"}
        )
        assert r.status_code in (401, 403), r.text


# ===========================================================================
#  RESILIENCIA (RES): LATENCIA ALTA Y FALLO DEL SUBSISTEMA B
# ===========================================================================
class TestRES_Resiliencia:
    """Caso 3 de la guía: inyectar latencia/fallo en el subsistema B (servicio/BD)
    y analizar si el subsistema A (capa HTTP) maneja el timeout o colapsa."""

    LATENCIA_SEG = 2.0

    def test_RES01_latencia_alta_en_creacion_de_pedido(self, cliente_api):
        """RES-01 | Inyectar 2s de latencia en order_service.create_order.
        Se mide si la capa HTTP impone un timeout o si bloquea hasta completar.
        HALLAZGO ESPERADO: no hay timeout server-side; el request bloquea y
        responde 201 tras la latencia (sin corte, sin circuit-breaker)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "RES01")
        h = _cliente_con_carrito(cliente_api, articulo, usuario="res01_user")

        from app.routers import orders as orders_router
        original = orders_router.order_service.create_order

        def lento(*args, **kwargs):
            time.sleep(self.LATENCIA_SEG)
            return original(*args, **kwargs)

        inicio = time.perf_counter()
        with patch.object(orders_router.order_service, "create_order", side_effect=lento):
            r = cliente_api.post(
                "/api/orders/", json={"delivery_address": "Calle Lenta 100"}, headers=h
            )
        elapsed = time.perf_counter() - inicio

        # El sistema NO colapsa (no 500) pero tampoco corta por timeout:
        assert r.status_code == 201, r.text
        assert elapsed >= self.LATENCIA_SEG, "La latencia inyectada no se aplicó"
        # Documentamos la ausencia de timeout como incidente RES-01.

    def test_RES02_fallo_del_subsistema_de_pago_no_expone_stacktrace(self, cliente_api):
        """RES-02 | El subsistema Pago lanza una excepción inesperada (fallo de BD).
        Se verifica que la capa HTTP degrada con 500 genérico SIN filtrar stacktrace
        ni detalles internos (resiliencia + seguridad de la frontera)."""
        _, articulo = _preparar_producto_con_stock(cliente_api, "RES02", precio=15.0)
        h, pedido = _crear_pedido_domicilio(cliente_api, articulo, usuario="res02_user", cantidad=1)

        from app.routers import payments as payments_router

        def revienta(*args, **kwargs):
            raise RuntimeError("psycopg2.OperationalError: connection reset by peer")

        with patch.object(payments_router.payment_service, "process_payment", side_effect=revienta):
            r = cliente_api.post(
                "/api/payments/",
                json={"order_id": pedido["id"], "amount": pedido["total_amount"],
                      "card_number": "4111111111111111", "cvv": "123"},
                headers=h,
            )
        assert r.status_code == 500, r.text
        cuerpo = r.text.lower()
        assert "psycopg2" not in cuerpo and "traceback" not in cuerpo and "connection reset" not in cuerpo, \
            "FUGA: el error interno se filtró al cliente"

    def test_RES03_integridad_tras_latencia_no_hay_doble_descuento(self, cliente_api):
        """RES-03 | Bajo latencia en el pedido, el stock se descuenta UNA sola vez
        (la lentitud no debe provocar reintentos/duplicados en la frontera Inventario)."""
        admin_h, articulo = _preparar_producto_con_stock(cliente_api, "RES03", stock=30)
        inv = cliente_api.get("/api/inventory/", headers=admin_h).json()
        inv_id = next(i["id"] for i in inv if i["menu_item_id"] == articulo["id"])
        h = _cliente_con_carrito(cliente_api, articulo, usuario="res03_user", cantidad=5)

        from app.routers import orders as orders_router
        original = orders_router.order_service.create_order

        def lento(*args, **kwargs):
            time.sleep(1.0)
            return original(*args, **kwargs)

        with patch.object(orders_router.order_service, "create_order", side_effect=lento):
            r = cliente_api.post(
                "/api/orders/", json={"delivery_address": "Calle Lenta 200"}, headers=h
            )
        assert r.status_code == 201, r.text

        inv_final = cliente_api.get(f"/api/inventory/{inv_id}", headers=admin_h).json()
        assert inv_final["stock"] == 25, f"Se esperaba 30-5=25 (una sola vez), real={inv_final['stock']}"
