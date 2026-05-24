# Documentación del Backend

Este directorio contiene el código fuente del servidor backend de la aplicación, construido sobre el framework **FastAPI** y utilizando **SQLAlchemy** para la interacción con la base de datos (SQLite).

## Arquitectura y Estructura

El patrón arquitectónico seguido en este backend se basa en la separación de responsabilidades a través de capas lógicas. Todo el código principal reside dentro del paquete `app/`:

### 1. Modelos (`app/models/`)
Contiene las entidades de la base de datos definidas mediante SQLAlchemy. Cada archivo representa una tabla en la base de datos y sus relaciones (por ejemplo, `User`, `Order`, `MenuItem`). Esta capa es estrictamente de representación de datos y no debe contener lógica de negocio.

### 2. Esquemas (`app/schemas/`)
Define las estructuras de validación de datos utilizando **Pydantic**. Estos esquemas actúan como contratos estrictos para los datos de entrada (Request) y salida (Response). Se utilizan para sanear, validar tipos y asegurar que el frontend no envíe cargas útiles malformadas.

### 3. Servicios (`app/services/`)
Aquí reside el **core lógico** de la aplicación (Lógica de Negocio). Los servicios orquestan las operaciones complejas (como calcular el precio de un envío, procesar un carrito o aplicar la máquina de estados de un pedido) y realizan las modificaciones directas en la base de datos importando los Modelos. 

### 4. Enrutadores (`app/routers/`)
Exponen las operaciones de los Servicios hacia el mundo exterior a través de Endpoints HTTP. Los enrutadores de FastAPI actúan como "Controladores": reciben las peticiones, validan la identidad del usuario, delegan la tarea a un Servicio específico y retornan un Esquema Pydantic.

### 5. Middleware y Utilidades
- **`app/middleware/`**: Interceptores globales, como el registro de tiempos de ejecución (`logging_middleware.py`), inyección de cabeceras CORS y manejo genérico de solicitudes.
- **`app/utils/`**: Funciones auxiliares y definición de Excepciones HTTP personalizadas (`exceptions.py`) para estandarizar las respuestas de error en toda la API.

## Flujo de Ejecución Típico
1. El cliente envía una petición HTTP que entra por un **Router** (`routers/`).
2. FastAPI valida los datos entrantes contra un **Schema** (`schemas/`) y verifica la autenticación.
3. El Router invoca a un **Service** (`services/`), pasándole la sesión de la base de datos.
4. El Service aplica las reglas de negocio e interactúa con la base de datos usando los **Models** (`models/`).
5. El resultado se serializa en un Schema de salida y el Router lo retorna al cliente.

## Ejecución del Servidor

Para iniciar el entorno de desarrollo, asegúrese de tener activado el entorno virtual (`.venv`) e instale las dependencias. Luego ejecute:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible por defecto en `http://127.0.0.1:8000`. La documentación interactiva (Swagger UI) autogenerada por FastAPI se puede consultar en `/docs`.

---

## Lógica de pedidos y roles (`app/services/order_service.py`)

El servicio de pedidos concentra la **máquina de estados**, los **permisos por rol** y efectos colaterales del negocio.

### Listado según rol (`list_orders_for_user`)

| Rol | Comportamiento |
|-----|----------------|
| `admin`, `cajero` | Devuelve todos los pedidos (`get_orders` sin filtrar por `user_id`) |
| `delivery` | Devuelve pedidos a domicilio (excluye «Recogida en local» / «Recojo en local») |
| `cliente` | Solo pedidos del usuario autenticado |

Implementado en el router `app/routers/orders.py` → `GET /api/orders/`.

### Actualización de estado (`update_order_status`)

Parámetros relevantes: `user_role`, `user_id` (para asignar repartidor al recoger).

| Rol | Transiciones permitidas (además de la máquina de estados) |
|-----|-------------------------------------------------------------|
| `admin` | Cualquier transición válida en `VALID_TRANSITIONS` |
| `cajero` | Cocina y cancelación; `LISTO`→`ENTREGADO` solo si es recojo en local |
| `delivery` | `LISTO`→`RECOGIDO`→`ENVIADO`→`ENTREGADO` solo en pedidos a domicilio |

El endpoint `PATCH /api/orders/{order_id}/status` admite roles: **`admin`**, **`cajero`**, **`delivery`** (vía `require_role` en el router).

### Efectos automáticos al cambiar estado

- **`LISTO`** (pedido a domicilio): crea registro en tabla `deliveries` si no existe (`_ensure_delivery_record`), con costo según `BASE_DELIVERY_FEE` y `DELIVERY_RATE_PER_KM` en `config.py`.
- **`RECOGIDO`** (rol `delivery`): asigna `driver_id` en la entrega vinculada (`_assign_delivery_driver`).
- **`CANCELADO`**: restaura stock en inventario (`_restore_inventory_on_cancel`).

### Estados canónicos (`app/models/order.py`)

```text
PENDIENTE → PREPARANDO → LISTO → RECOGIDO → ENVIADO → ENTREGADO
                ↓           ↓
            CANCELADO   CANCELADO / ENTREGADO (recojo local desde LISTO)
```

Valor de cancelación en API: **`CANCELADO`** (validado en `app/schemas/order.py` → `OrderStatusUpdate`).

---

## Módulo de entregas (`app/services/delivery_service.py`)

- **`POST /api/delivery/`**: creación manual (rol `admin`); valida que el pedido no sea recojo en local.
- **`GET /api/delivery/`**: `admin` ve todas; `delivery` ve entregas **sin asignar** o **asignadas a sí mismo** (`include_unassigned=True` en el listado).
- **`PATCH /api/delivery/{id}/status`**: actualiza estado de entrega y/o `driver_id`; el repartidor solo modifica entregas propias o sin asignar.

Estados de entrega: `ASIGNADO`, `RECOGIDO`, `EN_TRANSITO`, `ENTREGADO` (ver `app/schemas/delivery.py`).

---

## Archivos clave relacionados con el flujo operativo

| Archivo | Responsabilidad |
|---------|-----------------|
| `app/models/order.py` | `VALID_ORDER_STATES`, `VALID_TRANSITIONS` |
| `app/schemas/order.py` | Validación Pydantic del body `{ "status": "..." }` |
| `app/services/order_service.py` | Reglas de negocio, listado por rol, cancelación con stock |
| `app/routers/orders.py` | Endpoints REST de pedidos |
| `app/services/delivery_service.py` | CRUD y transiciones de entregas |
| `app/routers/delivery.py` | Endpoints REST de entregas |

---

## Seguridad (hardening)

| Módulo | Función |
|--------|---------|
| `app/services/auth_service.py` | Registro siempre con rol `cliente`; avatar URL con `quote` |
| `app/services/access_control.py` | Control de acceso a pagos y entregas (anti-IDOR) |
| `app/middleware/security.py` | Rate limit, cabeceras HTTP, idempotencia con TTL |
| `app/utils/sanitizer.py` | SQLi, XSS, path traversal |
| `app/utils/constants.py` | `INTERNAL_ERROR_DETAIL` para respuestas 500 |
| `app/config.py` | `AUTH_RATE_LIMIT_PER_MINUTE`, `CORS_ORIGINS`, `ENABLE_API_DOCS` |

### Autenticación

- `POST /api/auth/register`: rechaza roles desconocidos (`422`); ignora `admin`/`cajero`/`delivery` en body y persiste `cliente`.
- `POST /api/auth/login`: JWT incluye `sub` y `role`.
- `get_current_user`: valida que el rol del token coincida con el usuario en BD.

### Carrito e inventario

- `update_cart_item`: valida stock disponible antes de aumentar cantidad (responde `400` si no hay stock).
- `create_order`: bloqueo optimista de filas de inventario (`with_for_update`).
