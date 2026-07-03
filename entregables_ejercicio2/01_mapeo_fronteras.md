# Ejercicio Propuesto 2 — Mapeo de la Frontera

**Práctica 08 · Pruebas de Integración · Curso: Pruebas de Software**
**Proyecto:** NovaChef — Sistema SaaS de Restaurante + Delivery
**Arquitectura:** React + Vite (frontend) · FastAPI + SQLAlchemy + SQLite (backend)
**Herramienta de pruebas:** `pytest` + `FastAPI TestClient` (equivalente en Python de Supertest/Requests, versionable en el mismo repositorio)

---

## 1. Contexto

Según el Modelo en V, las pruebas de integración no verifican la lógica interna de un
módulo, sino que **exponen defectos en las interfaces y en la interacción entre
componentes**. Este documento cumple la **Tarea 1 (Mapeo de la Frontera)** del Ejercicio
Propuesto 2: identifica cada punto donde un **Subsistema A** entrega el control o los
datos a un **Subsistema B**, para luego atacar esas fronteras (Tarea 2) y documentar las
discrepancias (Tarea 3, ver `02_reportes_incidentes.md`).

El backend expone microservicios débilmente acoplados que se comunican mediante
**contratos explícitos** (schemas Pydantic + máquinas de estado). La integración se
prueba "en pequeña" (Small Integration): interfaces entre subsistemas internos del propio
software.

---

## 2. Diagrama de fronteras (flujo de datos del pedido)

```
  ┌──────────┐   F5: JWT + require_role (Auth/Roles gobierna TODAS las llamadas)
  │  CLIENTE │───────────────────────────────────────────────────────────────┐
  └────┬─────┘                                                                │
       │ POST /api/cart/                                                      │
       ▼                                                                      ▼
  ┌──────────┐   F1     ┌──────────┐   F3     ┌──────────┐              ┌───────────┐
  │ CARRITO  │─────────▶│  PEDIDO  │─────────▶│   PAGO   │              │   AUTH /  │
  │ (Cart)   │ checkout │ (Order)  │  cobro   │(Payment) │              │   ROLES   │
  └────┬─────┘          └────┬─────┘          └──────────┘              └───────────┘
       │ F2: valida stock    │ F2: descuenta       │ F4: despacho
       ▼                     ▼ stock               ▼
  ┌──────────────────────────────────┐      ┌──────────┐
  │          INVENTARIO              │      │ DELIVERY │
  │          (Inventory)            │      │ + máquina│
  └──────────────────────────────────┘      │ de estado│
                                             └──────────┘
```

---

## 3. Fronteras identificadas (Subsistema A → Subsistema B)

| ID | Frontera (A → B) | Punto exacto de handoff | Contrato / regla en la interfaz |
|----|------------------|--------------------------|----------------------------------|
| **F1** | **Carrito → Pedido** | `POST /api/orders/` → `order_service.create_order()` lee los `CartItem` del usuario y construye el `Order` | Carrito no vacío · precios "congelados" (snapshot) · total ≤ $5000 · vacía el carrito al finalizar |
| **F2** | **Pedido → Inventario** | `create_order()` (`order_service.py:186-239`) valida y descuenta `Inventory.stock`; `add_to_cart()` (`cart_service.py:28`) valida stock al agregar | `stock ≥ cantidad` en dos capas (defensa en profundidad) · descuento atómico `with_for_update()` · restauración de stock al CANCELAR |
| **F3** | **Pedido → Pago** | `POST /api/payments/` → `payment_service.process_payment()` lee el `Order` referido por `order_id` | Pedido existe · pertenece al usuario · estado = `PENDIENTE` · sin pago previo · `amount == total_amount` (±0.01) · tarjeta 16 dígitos + Luhn + CVV |
| **F4** | **Pedido → Delivery** | `POST /api/delivery/` → `delivery_service.create_delivery()` + máquina de estados `PATCH /api/orders/{id}/status` | Pedido no `PENDIENTE`/`CANCELADO` · no es "recojo en local" · sin entrega previa · `0.5 ≤ distance_km ≤ 20` · transiciones válidas (`VALID_TRANSITIONS`) |
| **F5** | **Auth/Roles → Operaciones** | Dependencias `get_current_user` / `require_role(...)` ejecutadas ANTES de ceder control al subsistema de negocio en cada router | JWT válido y no expirado · rol autorizado por endpoint (admin / cajero / cliente / delivery) · "cerrado por defecto" |

---

## 4. Máquinas de estado en las fronteras (contratos de comportamiento)

**Pedido (`Order.status`) — frontera F4:**

```
PENDIENTE ─▶ PREPARANDO ─▶ LISTO ─▶ RECOGIDO ─▶ ENVIADO ─▶ ENTREGADO
    │            │           │
    └────────────┴───────────┴──▶ CANCELADO   (ENTREGADO y CANCELADO son terminales)
```

**Entrega (`Delivery.status`):**

```
ASIGNADO ─▶ RECOGIDO ─▶ EN_TRANSITO ─▶ ENTREGADO
```

Cualquier salto que no respete estas transiciones es un **fallo semántico de interfaz**
(ver casos SEM-11).

---

## 5. Riesgos de integración por frontera (análisis predictivo)

| Frontera | Riesgo principal | Categoría de inyección aplicada |
|----------|------------------|----------------------------------|
| F1 | Desajuste de datos (tipo/tamaño) al construir el pedido | Sintáctico (SIN-01, SIN-02) + Semántico (SEM-01, SEM-02) |
| F2 | Sobreventa / descuento incorrecto de stock | Semántico (SEM-03, SEM-04) |
| F3 | Cobro por monto erróneo, doble cobro, cobro de pedido ajeno | Sintáctico (SIN-03..05) + Semántico (SEM-05..08) |
| F4 | Despacho de pedidos no listos o de recojo en local; saltos de estado | Sintáctico (SIN-06, SIN-07) + Semántico (SEM-09..11) |
| F5 | Escalada de privilegios / acceso sin credencial | Semántico (SEM-12, SEM-13) + Sintáctico (SIN-08) |
| Todas | Latencia alta / caída del subsistema B | Resiliencia (RES-01, RES-02, RES-03) |

> Se diseñaron **24 casos de prueba** (la guía exige un mínimo de 3). Cobertura por
> categoría: **8 Sintácticos**, **13 Semánticos**, **3 de Resiliencia**, distribuidos en
> las 5 fronteras. Detalle de resultados en `02_reportes_incidentes.md` y evidencia de
> ejecución en `03_salida_terminal.txt` / `reporte_html/`.
