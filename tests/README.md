# Documentación de Pruebas (Testing Suite)

Este directorio contiene la batería de pruebas de la aplicación, diseñada para garantizar la estabilidad, la seguridad y el correcto funcionamiento del software ante cualquier cambio. Las pruebas están implementadas bajo el framework **Pytest**.

## Estructura de las Pruebas

El sistema de testing está organizado por dominios lógicos para facilitar la mantenibilidad y la rápida detección de regresiones:

### 1. Pruebas Unitarias por Dominio
Archivos dedicados a probar en aislamiento los diferentes módulos del Backend (especialmente los endpoints de FastAPI y los Servicios).
- `test_auth.py`: Valida los registros, inicios de sesión y manejo correcto de roles (Tokens JWT).
- `test_cart.py`: Evalúa el comportamiento del carrito de compras, adición, eliminación y límites lógicos.
- `test_delivery.py`: Comprueba el flujo de entregas, cálculos de distancia y estimación de tiempo.
- `test_inventory.py`: Asegura que el inventario descuente correctamente al confirmar un pedido y respete el stock disponible.
- `test_menu.py`: Prueba las operaciones CRUD sobre el catálogo de platillos.
- `test_orders.py`: Verifica la máquina de estados de los pedidos (Pendiente -> Preparando -> Listo -> Entregado) y transiciones inválidas; incluye cancelación con estado **`CANCELADO`** (valor canónico de la API).
- `test_payments.py`: Valida el procesamiento de pagos, formatos de tarjeta y algoritmos tipo Luhn.

### 2. Pruebas de Integración (`test_integration.py`)
Asegura que los componentes funcionen armónicamente en conjunto. En lugar de probar una función aislada, simula el flujo de vida completo de un usuario real (Login -> Explorar Menú -> Añadir al Carrito -> Pagar -> Pedido Completado).

### 3. Pruebas de Seguridad y Estrés
- `test_security.py`: Garantiza que el sistema está blindado contra ataques comunes (fuerza bruta, payloads gigantes, inyecciones) devolviendo los códigos HTTP correctos (`401`, `422`).
- `test_massive_attacks.py` / `test_massive_bva_ep.py`: Casos de prueba exhaustivos (Análisis de Valores Límite y Particiones de Equivalencia) para someter al sistema a datos extremos.

## Configuración y Ejecución

Las pruebas se ejecutan sobre una base de datos temporal (configurada mediante un _fixture_ en `conftest.py` en la raíz) para evitar que los tests alteren los datos de producción o desarrollo.

Para ejecutar la batería completa de pruebas:

```bash
pytest -v
```

Para ejecutar pruebas de un archivo específico:
```bash
pytest -v tests/test_orders.py
```

## Convenciones
- **Nomenclatura:** Todo archivo de prueba debe comenzar con el prefijo `test_`.
- **Independencia:** Cada test está diseñado para limpiar su propio estado al finalizar, previniendo que la ejecución de una prueba afecte a otra.

---

## Cobertura del flujo operativo por rol

Las pruebas validan comportamiento alineado con la lógica de negocio documentada en el README raíz:

| Área | Archivo(s) | Qué se verifica |
|------|------------|-----------------|
| Máquina de estados | `test_orders.py` | Transiciones válidas/inválidas; cancelación con `CANCELADO` |
| Entregas | `test_delivery.py` | Creación, costos por distancia, asignación de repartidor, transiciones de entrega |
| Flujo E2E | `test_integration.py` | Login → menú → carrito → pedido → pago/entrega → estados |
| Seguridad | `test_security.py` | Payloads maliciosos, respuestas `401`/`422` |
| OWASP / regresión | `test_owasp_hardening.py` | Rol público, IDOR, `CANCELADO`, idempotencia, pago cash |
| Carrito | `test_cart.py` | Stock al actualizar: `400` si cantidad > inventario |
| EP / BVA | `test_massive_bva_ep.py`, `test_massive_attacks.py` | Límites de entrada y estrés |

### Estados de pedido en las pruebas

Los tests deben usar los mismos literales que el backend (`app/models/order.py`):

```text
PENDIENTE | PREPARANDO | LISTO | RECOGIDO | ENVIADO | ENTREGADO | CANCELADO
```

Ejemplo de body en `PATCH /api/orders/{id}/status`:

```json
{ "status": "CANCELADO" }
```

### Ejecución focalizada por dominio operativo

```bash
# Pedidos y cancelación
pytest -v tests/test_orders.py

# Repartidor y entregas
pytest -v tests/test_delivery.py

# Flujo completo de negocio
pytest -v tests/test_integration.py
```

Tras cambios en `order_service.py` o en el frontend (`orderStatus.js`), conviene ejecutar al menos estos archivos antes de publicar.

---

## Fixtures de staff (`conftest.py`)

Usuarios `admin`, `cajero` y `delivery` se crean en la **BD de prueba** (`TestingSessionLocal`), no vía registro público, para reflejar el comportamiento real de producción.

```bash
pytest -v tests/test_owasp_hardening.py
pytest -v tests/test_auth.py::TestRegistroEP::test_registrar_rol_invalido
pytest -v tests/test_cart.py::TestCarritoCasosExtremos::test_actualizar_exceeding_stock
```
