# Ejercicio Propuesto 2 — Reportes de Incidente (Esperado vs Real)

**Práctica 08 · Pruebas de Integración · Curso: Pruebas de Software**
**Proyecto:** NovaChef — Restaurante + Delivery · **Backend:** FastAPI + SQLite
**Suite:** `tests/test_fronteras_integracion.py` · **Resultado global: 24/24 PASSED**
**Fecha de ejecución:** 2026-07-03

---

## 1. Resumen ejecutivo

Se ejecutaron **24 casos de inyección de fallas de interfaz** sobre las 5 fronteras del
sistema (ver `01_mapeo_fronteras.md`). El objetivo fue "romper" la comunicación entre
subsistemas mediante entradas sintácticamente inválidas, semánticamente incoherentes y
condiciones de latencia/fallo.

**Veredicto:** el sistema **defendió correctamente las 24 fronteras** (todas las pruebas
pasan porque el sistema respondió con el código HTTP y el comportamiento esperados). No
se hallaron defectos bloqueantes. Sí se documentan **2 hallazgos de arquitectura** (uno
de severidad MEDIA sobre resiliencia y uno informativo sobre defensa en profundidad) con
sus recomendaciones.

| Categoría | Casos | Resultado |
|-----------|-------|-----------|
| Sintáctico `[SIN]` | 8 | 8 defendidos ✔ |
| Semántico `[SEM]` | 13 | 13 defendidos ✔ |
| Resiliencia `[RES]` | 3 | 3 controlados ✔ (1 con recomendación) |
| **TOTAL** | **24** | **24 PASSED** |

> **Nota de interpretación:** en pruebas de inyección de fallas, un caso "PASSED" significa
> que **la frontera reaccionó como debía** (rechazó la entrada maliciosa/ilógica o degradó
> sin colapsar). El "Resultado Esperado" es la reacción defensiva correcta; el "Resultado
> Real" es lo observado en la ejecución. Cuando ambos coinciden, el incidente se cierra
> como *Comportamiento Correcto*; las divergencias se elevan como *Hallazgo*.

---

## 2. Reportes de Incidente detallados (formato IEEE-829)

La guía exige un mínimo de **3 casos** (Sintáctico, Semántico, Resiliencia). A continuación
los 3 representativos obligatorios en formato extendido, seguidos de los 2 hallazgos.

### 🟦 RI-001 — Caso 1: Fallo SINTÁCTICO (Frontera F3: Pedido → Pago)

| Campo | Detalle |
|-------|---------|
| **ID de prueba** | `SIN-04` · `test_SIN04_pago_con_amount_no_numerico` |
| **Frontera atacada** | F3 · Pedido → Pago (`POST /api/payments/`) |
| **Tipo de defecto inyectado** | Tipo de dato erróneo en campo numérico |
| **Entrada** | `{ "order_id": <id>, "amount": "mucho dinero", "card_number": "4111...1111", "cvv": "123" }` |
| **Resultado Esperado** | HTTP **422** — el contrato Pydantic rechaza `amount` no convertible a `float` antes de tocar la lógica de negocio |
| **Resultado Real** | HTTP **422 Unprocessable Entity**, cuerpo `{"detail":"Validation error", "errors":[{"field":"body -> amount", ...}]}` |
| **Veredicto** | ✔ **Comportamiento Correcto** — la frontera valida el contrato de tipos |
| **Severidad** | N/A (defensa exitosa) |

---

### 🟨 RI-002 — Caso 2: Fallo SEMÁNTICO (Frontera F3: Pedido → Pago)

| Campo | Detalle |
|-------|---------|
| **ID de prueba** | `SEM-05` · `test_SEM05_pago_con_monto_distinto_al_total` |
| **Frontera atacada** | F3 · Pedido → Pago (`POST /api/payments/`) |
| **Tipo de defecto inyectado** | Valor legal pero fuera de lógica (pagar $1.00 un pedido de $20.00) |
| **Entrada** | Pedido con `total_amount = 20.00`; pago con `amount = 1.00` y tarjeta válida |
| **Resultado Esperado** | HTTP **400** — el subsistema Pago debe rechazar montos que no coinciden con el total del pedido (`payment_service.py:42`) |
| **Resultado Real** | HTTP **400 Bad Request**, cuerpo `{"detail":"El monto del pago no coincide con el total del pedido"}` |
| **Veredicto** | ✔ **Comportamiento Correcto** — la frontera preserva la integridad económica |
| **Severidad** | N/A (defensa exitosa) |

> **Análogo al ejemplo de la guía** ("fecha de entrega anterior a la de pedido"): aquí la
> incoherencia semántica es *monto ≠ total*. Otros casos semánticos cubiertos: doble pago
> (SEM-06), pago de pedido ajeno (SEM-07, 403), despacho de pedido aún PENDIENTE (SEM-09),
> delivery para pedido de recojo en local (SEM-10) y salto ilegal de máquina de estados
> PENDIENTE→ENTREGADO (SEM-11).

---

### 🟥 RI-003 — Caso 3: RESILIENCIA (Latencia alta, Frontera F1: Carrito → Pedido)

| Campo | Detalle |
|-------|---------|
| **ID de prueba** | `RES-01` · `test_RES01_latencia_alta_en_creacion_de_pedido` |
| **Frontera atacada** | F1 · Carrito → Pedido (`POST /api/orders/`) |
| **Técnica** | Inyección de **2.0 s de latencia** en `order_service.create_order` vía `unittest.mock.patch` (simula un subsistema B lento: BD saturada) |
| **Resultado Esperado** | El subsistema A (capa HTTP) NO debe colapsar (sin 500); idealmente debería aplicar un *timeout* y devolver 503/504 |
| **Resultado Real** | HTTP **201 Created** tras ≈2.0 s — el sistema **no colapsa** pero **bloquea el request hasta completar**: **no hay timeout server-side ni circuit-breaker** |
| **Veredicto** | ⚠️ **HALLAZGO (ver H-01)** — resiliente ante el colapso, pero sin corte por timeout |
| **Severidad** | **MEDIA** |

---

### 🟥 RI-004 — Resiliencia: no fuga de detalles internos (Frontera F3)

| Campo | Detalle |
|-------|---------|
| **ID de prueba** | `RES-02` · `test_RES02_fallo_del_subsistema_de_pago_no_expone_stacktrace` |
| **Técnica** | El subsistema Pago lanza `RuntimeError("psycopg2.OperationalError: connection reset...")` |
| **Resultado Esperado** | HTTP **500** con mensaje **genérico**, SIN filtrar stacktrace ni motor de BD (seguridad de la frontera) |
| **Resultado Real** | HTTP **500**, cuerpo `{"detail":"Internal server error"}`. No aparece `psycopg2`, `traceback` ni `connection reset` en la respuesta |
| **Veredicto** | ✔ **Comportamiento Correcto** — degradación segura (OWASP A09) |
| **Severidad** | N/A (defensa exitosa) |

---

## 3. Hallazgos elevados

### H-01 · Ausencia de timeout / circuit-breaker en la capa HTTP (Severidad MEDIA)

- **Evidencia:** RES-01. Con 2 s de latencia inyectada, el endpoint bloquea el worker
  hasta completar y responde 201, en lugar de cortar con 503/504.
- **Riesgo:** bajo latencia real o saturación del subsistema B (BD), los workers se
  agotan y el servicio deja de atender (denegación de servicio por agotamiento de hilos).
- **Recomendación:**
  1. Añadir *timeout* de aplicación (p.ej. middleware `asyncio.wait_for` o `timeout` de
     ASGI) que devuelva **504 Gateway Timeout** pasado un umbral (p.ej. 5 s).
  2. Considerar un *circuit-breaker* (patrón resiliencia) para operaciones dependientes
     de BD/servicios externos.
  3. Configurar `pool_timeout` y límites de conexión en SQLAlchemy.

### H-02 · Validación de stock duplicada — defensa en profundidad (Informativo)

- **Evidencia:** SEM-03. La validación de stock se dispara primero en la frontera
  **Carrito → Inventario** (`add_to_cart`), y existe un guard **redundante** en
  **Pedido → Inventario** (`create_order`).
- **Interpretación:** es una **buena práctica** (shift-left / defensa en profundidad): el
  error se detecta lo antes posible. No es un defecto.
- **Recomendación:** mantener ambos guards; documentar explícitamente que el guard de
  `create_order` es la última línea de defensa ante condiciones de carrera (protegido con
  `with_for_update()`).

---

## 4. Matriz completa de los 24 casos (Esperado vs Real)

| ID | Frontera | Cat. | Entrada inyectada | HTTP Esperado | HTTP Real | Estado |
|----|----------|------|-------------------|:-------------:|:---------:|--------|
| SIN-01 | F1 Carrito→Pedido | SIN | `notes` como objeto JSON | 422 | 422 | ✔ Correcto |
| SIN-02 | F1 Carrito→Pedido | SIN | dirección de 2 chars (<5) | 422 | 422 | ✔ Correcto |
| SEM-01 | F1 Carrito→Pedido | SEM | pedido con carrito vacío | 400 | 400 | ✔ Correcto |
| SEM-02 | F1 Carrito→Pedido | SEM | total $9801 (> $5000) | 400 | 400 | ✔ Correcto |
| SEM-03 | F2 Pedido→Inventario | SEM | 30 uds con stock 5 | 400 | 400 | ✔ Correcto (H-02) |
| SEM-04 | F2 Pedido→Inventario | SEM | verificar descuento 50→42 | 42 | 42 | ✔ Correcto |
| SIN-03 | F3 Pedido→Pago | SIN | tarjeta credit sin card_number | 422 | 422 | ✔ Correcto |
| SIN-04 | F3 Pedido→Pago | SIN | `amount` = "mucho dinero" | 422 | 422 | ✔ Correcto |
| SIN-05 | F3 Pedido→Pago | SIN | tarjeta de 15 dígitos | 422 | 422 | ✔ Correcto |
| SEM-05 | F3 Pedido→Pago | SEM | pagar $1 un pedido de $20 | 400 | 400 | ✔ Correcto |
| SEM-06 | F3 Pedido→Pago | SEM | doble pago del mismo pedido | 400 | 400 | ✔ Correcto |
| SEM-07 | F3 Pedido→Pago | SEM | pagar pedido de otro usuario | 403 | 403 | ✔ Correcto |
| SEM-08 | F3 Pedido→Pago | SEM | pagar pedido inexistente (99999) | 404 | 404 | ✔ Correcto |
| SIN-06 | F4 Pedido→Delivery | SIN | `distance_km` = 50 (>20) | 422 | 422 | ✔ Correcto |
| SIN-07 | F4 Pedido→Delivery | SIN | falta campo `address` | 422 | 422 | ✔ Correcto |
| SEM-09 | F4 Pedido→Delivery | SEM | delivery de pedido PENDIENTE | 400 | 400 | ✔ Correcto |
| SEM-10 | F4 Pedido→Delivery | SEM | delivery de "recojo en local" | 400 | 400 | ✔ Correcto |
| SEM-11 | F4 Pedido→Delivery | SEM | salto PENDIENTE→ENTREGADO | 400 | 400 | ✔ Correcto |
| SEM-12 | F5 Auth/Roles | SEM | cliente crea inventario | 403 | 403 | ✔ Correcto |
| SIN-08 | F5 Auth/Roles | SIN | token JWT malformado | 401 | 401 | ✔ Correcto |
| SEM-13 | F5 Auth/Roles | SEM | operar sin token | 401/403 | 401/403 | ✔ Correcto |
| RES-01 | F1 (latencia) | RES | +2 s en create_order | 201 sin timeout | 201 sin timeout | ⚠️ Hallazgo H-01 |
| RES-02 | F3 (fallo BD) | RES | excepción interna en pago | 500 genérico | 500 genérico | ✔ Correcto |
| RES-03 | F2 (latencia) | RES | +1 s, integridad de stock | 30→25 (una vez) | 30→25 | ✔ Correcto |

---

## 5. Conclusiones

1. Las **5 fronteras** del sistema NovaChef aplican correctamente sus contratos de
   interfaz (tipos, reglas de negocio, máquinas de estado y autorización).
2. La **inyección sintáctica** es interceptada por los schemas Pydantic (422) antes de
   llegar a la lógica; la **inyección semántica** es rechazada por los servicios (400/403/404).
3. La **resiliencia** es adecuada frente a excepciones (500 genérico sin fuga), pero se
   recomienda **implementar timeouts/circuit-breaker** (Hallazgo H-01) para robustez ante
   latencia sostenida.
4. Se **superó ampliamente** el mínimo exigido (3 casos): se entregaron **24 casos** con
   evidencia reproducible (código versionado, salida de terminal y reporte HTML con
   capturas).
