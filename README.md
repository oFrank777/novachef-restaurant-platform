# Guerra de Testers — Restaurante Delivery

Sistema **full-stack** para la gestión de un restaurante con pedidos en línea, pagos, inventario, entregas y reportes. El proyecto está pensado como plataforma de aprendizaje y competencia en **calidad de software**: incluye API robusta, interfaz web por roles y una batería extensa de pruebas automatizadas (unitarias, integración, seguridad y análisis BVA/EP).

| Capa | Tecnología |
|------|------------|
| **Backend** | Python 3 · FastAPI · SQLAlchemy · SQLite |
| **Frontend** | React 19 · Vite 8 · React Router · Axios |
| **Pruebas** | pytest · FastAPI TestClient |
| **Autenticación** | JWT · RBAC (4 roles) |

---

## Tabla de contenidos

1. [Características principales](#características-principales)
2. [Estructura del repositorio](#estructura-del-repositorio)
3. [Requisitos previos](#requisitos-previos)
4. [Instalación y puesta en marcha](#instalación-y-puesta-en-marcha)
5. [Usuarios de demostración](#usuarios-de-demostración)
6. [Roles y permisos](#roles-y-permisos)
7. [Flujo operativo empresarial](#flujo-operativo-empresarial)
8. [Estados de pedido y convenciones](#estados-de-pedido-y-convenciones)
9. [Módulos del sistema](#módulos-del-sistema)
10. [Ejecución de pruebas](#ejecución-de-pruebas)
11. [Seguridad y hardening (OWASP)](#seguridad-y-hardening-owasp)
12. [Documentación adicional](#documentación-adicional)
13. [Variables de entorno](#variables-de-entorno)
14. [Archivos ignorados por Git](#archivos-ignorados-por-git)
15. [Publicar en GitHub](#publicar-en-github)
16. [Checklist antes de publicar en GitHub](#checklist-antes-de-publicar-en-github)

---

## Características principales

- **Control de acceso basado en roles (RBAC)** para `admin`, `cajero`, `cliente` y `delivery`.
- **Catálogo de menú** con categorías, precios y disponibilidad.
- **Carrito y pedidos** con máquina de estados estricta (transiciones válidas e inválidas).
- **Inventario** vinculado al menú; descuento de stock al confirmar pedidos.
- **Pagos** simulados con validación de tarjeta (incluye algoritmo de Luhn).
- **Entregas** con cálculo de tarifa y tiempo estimado según distancia; registro automático al marcar pedido a domicilio como `LISTO`.
- **Flujo operativo por rol** (cliente → cajero → repartidor) integrado en API y UI.
- **Reportes** para administración.
- **Seguridad en API**: rate limiting, cabeceras de seguridad, idempotencia, sanitización y manejo centralizado de errores.
- **Suite de pruebas** con cobertura por dominio, integración, seguridad y casos masivos BVA/EP.

---

## Estructura del repositorio

```
GUERRA DE TESTERS/
│
├── backend/                    # Servidor API (FastAPI)
│   ├── app/
│   │   ├── models/             # Entidades SQLAlchemy (User, Order, MenuItem, …)
│   │   ├── schemas/            # Contratos Pydantic (request/response)
│   │   ├── services/           # Lógica de negocio
│   │   ├── routers/            # Endpoints HTTP (/api/auth, /api/orders, …)
│   │   ├── middleware/         # Logging, rate limit, seguridad, idempotencia
│   │   ├── utils/              # Seguridad, sanitización, excepciones
│   │   ├── config.py           # Configuración (env + valores por defecto)
│   │   ├── database.py         # Conexión y sesión SQLAlchemy
│   │   ├── seed.py             # Usuarios y menú inicial
│   │   └── main.py             # Punto de entrada de la aplicación
│   ├── requirements.txt        # Dependencias Python del backend
│   └── README.md               # Documentación detallada del backend
│
├── frontend/                   # Cliente web (React + Vite)
│   ├── src/
│   │   ├── pages/              # Pantallas (Login, Menú, Pedidos, Entrega, …)
│   │   ├── components/         # UI reutilizable y layout
│   │   ├── context/            # Auth, carrito, tema
│   │   ├── api/                # Cliente Axios hacia /api
│   │   ├── constants/          # Constantes compartidas (p. ej. orderStatus.js)
│   │   ├── styles/             # Estilos globales y tokens de diseño
│   │   └── utils/              # Utilidades (p. ej. eventEmitter)
│   ├── vite.config.js          # Proxy /api → localhost:8000
│   ├── package.json
│   └── README.md               # Documentación detallada del frontend
│
├── tests/                      # Pruebas automatizadas (pytest)
│   ├── conftest.py             # Fixtures: BD en memoria, TestClient
│   ├── test_auth.py            # Autenticación y JWT
│   ├── test_cart.py            # Carrito
│   ├── test_menu.py            # Menú CRUD
│   ├── test_orders.py          # Pedidos y estados
│   ├── test_payments.py        # Pagos
│   ├── test_inventory.py       # Inventario
│   ├── test_delivery.py        # Entregas
│   ├── test_integration.py     # Flujos end-to-end
│   ├── test_security.py        # Vectores de ataque
│   ├── test_massive_*.py       # BVA, EP y estrés
│   ├── test_owasp_hardening.py # Regresiones OWASP (roles, IDOR, idempotencia)
│   └── README.md               # Guía de la suite de pruebas
│
├── .env.example                # Plantilla de variables (copiar a .env)
│
├── docs/                       # Documentación de proyecto
│   ├── api_documentation.md    # Referencia completa de endpoints
│   ├── user_manual.md          # Manual de usuario e instalación
│   └── testing_document.md     # Estrategia EP/BVA y catálogo de pruebas
│
├── .gitignore                  # Exclusiones globales del repositorio
└── README.md                   # Este archivo
```

---

## Requisitos previos

- **Python** 3.10 o superior
- **Node.js** 20+ y **npm**
   - Se sugiere usar el instalador de **NVM for Windows** para mantener la última versión estable de Node.js y facilitar la administración de versiones del entorno.
   - Descarga del instalador:
     - [NVM for Windows Releases](https://github.com/coreybutler/nvm-windows/releases)
   - Instalar el archivo `nvm-setup.exe` y luego ejecutar:

```bash
nvm install latest
nvm use latest
```

- **Git** (para clonar y publicar el repositorio)

---

## Instalación y puesta en marcha

### 1. Clonar el repositorio

```bash
git clone <URL-de-tu-repositorio>
cd "novachef-restaurant-platform"
```

### 2. Backend (API)

Desde la raíz del proyecto:

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -r backend/requirements.txt
```

Iniciar el servidor (ejecutar desde la carpeta `backend/`):

```bash
cd backend
uvicorn app.main:app --reload
```

| Recurso | URL |
|---------|-----|
| API raíz | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

Al arrancar, la API crea la base de datos SQLite (`restaurant.db` en el directorio de trabajo del backend) y ejecuta el **seed** de usuarios y platillos si la BD está vacía.

### 3. Frontend (interfaz web)

En otra terminal, desde la raíz:

```bash
cd frontend
npm install
npm run dev
```

| Recurso | URL |
|---------|-----|
| Aplicación web | http://localhost:5173 |

Vite redirige las peticiones `/api/*` al backend en el puerto `8000` (ver `frontend/vite.config.js`).

### 4. Flujo recomendado de desarrollo

1. Levantar **backend** (`uvicorn` en `backend/`).
2. Levantar **frontend** (`npm run dev` en `frontend/`).
3. Abrir http://localhost:5173 e iniciar sesión con un usuario de demostración (ver tabla siguiente).

---

## Usuarios de demostración

Tras el primer arranque del backend, se crean automáticamente estos usuarios (si no existen registros previos):

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `Admin123` | Administrador |
| `cliente1` | `Cliente123` | Cliente |
| `cajero1` | `Cajero123` | Cajero |
| `delivery1` | `Delivery123` | Repartidor |

> **Nota de seguridad:** Son credenciales de desarrollo. No uses estas contraseñas en producción.

El menú incluye más de 20 platillos de ejemplo (pizzas, hamburguesas, bebidas, postres, etc.) con inventario inicial de 50 unidades por ítem.

---

## Roles y permisos

| Rol | Descripción resumida |
|-----|----------------------|
| **admin** | Acceso completo: menú, inventario, pedidos, pagos, entregas y reportes. |
| **cajero** | Gestión operativa de pedidos y pagos en mostrador. |
| **cliente** | Explorar menú, carrito, realizar pedidos y pagos propios. |
| **delivery** | Ver y actualizar entregas asignadas. |

La interfaz y la API validan el rol en cada operación sensible. Detalle de pantallas y flujos en [`docs/user_manual.md`](docs/user_manual.md).

### Visibilidad de pedidos en la API (`GET /api/orders/`)

| Rol | Qué pedidos ve |
|-----|----------------|
| **admin** | Todos los pedidos del negocio |
| **cajero** | Todos los pedidos del negocio (cola de cocina y mostrador) |
| **delivery** | Solo pedidos a **domicilio** (con dirección distinta de «Recogida en local») |
| **cliente** | Solo sus propios pedidos |

### Quién puede cambiar el estado (`PATCH /api/orders/{id}/status`)

| Rol | Transiciones permitidas |
|-----|-------------------------|
| **admin** | Todas las transiciones válidas de la máquina de estados |
| **cajero** | Cocina: `PENDIENTE`→`PREPARANDO`→`LISTO`; cancelar; mostrador: `LISTO`→`ENTREGADO` (solo recojo en local) |
| **delivery** | Ruta: `LISTO`→`RECOGIDO`→`ENVIADO`→`ENTREGADO` (solo pedidos a domicilio) |
| **cliente** | No puede cambiar estados operativos |

---

## Flujo operativo empresarial

Flujo de punta a punta recomendado para probar el negocio completo en local:

```
Cliente                    Cajero                         Repartidor
   │                          │                                │
   ├─ Menú / Carrito          │                                │
   ├─ Crear pedido ──────────►│                                │
   │  (con dirección o        │                                │
   │   «Recogida en local»)   │                                │
   │                          ├─ PENDIENTE → PREPARANDO        │
   │                          ├─ PREPARANDO → LISTO            │
   │                          │   (si es domicilio: se crea   │
   │                          │    registro en /api/delivery)  │
   │                          │                                │
   │                          │  [Recojo local]                ├─ LISTO → RECOGIDO
   │                          ├─ LISTO → ENTREGADO            ├─ RECOGIDO → ENVIADO
   │                          │                                ├─ ENVIADO → ENTREGADO
   │◄─ Pedido completado ─────┴────────────────────────────────┘
```

### Pasos de demostración rápida

1. **Cliente** (`cliente1` / `Cliente123`): añadir productos al carrito y crear pedido con **dirección real** (mín. 5 caracteres), no «Recogida en local».
2. **Cajero** (`cajero1` / `Cajero123`): ir a **Pedidos** → avanzar a *En preparación* → *Listo*.
3. **Repartidor** (`delivery1` / `Delivery123`): ir a **Entregas** → seleccionar pedido *Listo* → *Recogido* → *En camino* → *Entregado*.
4. **Cancelación (cajero/admin):** en estados `PENDIENTE` o `PREPARANDO`, usar el botón de cancelar; el estado enviado debe ser `CANCELADO` (el backend restaura el inventario).

Pantallas clave por rol: **Panel** (`/dashboard`), **Pedidos** (`/orders`), **Entregas** (`/delivery`), **Pagos** (`/payments` — admin y cajero).

---

## Estados de pedido y convenciones

Los estados del pedido están definidos en **español** y en **MAYÚSCULAS** en backend y frontend. El valor canónico para cancelación es **`CANCELADO`** (no usar `CANCELLED`; provoca error **422** de validación).

| Estado | Significado |
|--------|-------------|
| `PENDIENTE` | Pedido recién creado |
| `PREPARANDO` | En cocina |
| `LISTO` | Listo para recoger o enviar |
| `RECOGIDO` | Repartidor recogió el pedido en el local |
| `ENVIADO` | En camino al cliente |
| `ENTREGADO` | Entregado (estado final) |
| `CANCELADO` | Cancelado (estado final; stock restaurado) |

**Transiciones válidas** (resumen): ver `backend/app/models/order.py` (`VALID_TRANSITIONS`) y `frontend/src/constants/orderStatus.js` (`getNextStatuses`).

**Constantes compartidas en el frontend:** `frontend/src/constants/orderStatus.js` centraliza etiquetas, colores y reglas de botones por rol para evitar desincronización con la API.

---

## Módulos del sistema

| Módulo | Backend (`/api/...`) | Frontend (ruta) |
|--------|----------------------|-----------------|
| Autenticación | `/api/auth` | `/login`, `/register` |
| Menú | `/api/menu` | `/menu` |
| Carrito | `/api/cart` | `/cart` |
| Pedidos | `/api/orders` | `/orders` (también visible para `delivery` en modo consulta/coordinación) |
| Pagos | `/api/payments` | `/payments` |
| Inventario | `/api/inventory` | `/inventory` |
| Entregas | `/api/delivery` | `/delivery` |
| Reportes | `/api/reports` | `/reports` |
| Panel | — | `/dashboard` |

---

## Ejecución de pruebas

Las pruebas usan una **base de datos SQLite en memoria**; no modifican `restaurant.db` de desarrollo.

Desde la **raíz del proyecto**, con el entorno virtual activado y dependencias instaladas:

```bash
pytest -v
```

Ejemplos útiles:

```bash
# Un archivo concreto
pytest -v tests/test_orders.py

# Pruebas de seguridad
pytest -v tests/test_security.py

# Con resumen de fallos
pytest -v --tb=short
```

Más contexto en [`tests/README.md`](tests/README.md) y [`docs/testing_document.md`](docs/testing_document.md).

---

## Seguridad y hardening (OWASP)

| Control | Implementación |
|---------|----------------|
| **Broken Access Control** | `list_orders_for_user`, `user_can_view_order`, `access_control.py`, rutas `ProtectedRoute` por rol en React |
| **Registro público** | Rol forzado a `cliente`; roles inválidos → `422`; roles privilegiados en body ignorados |
| **JWT** | Claim `role` en token; verificación en `get_current_user`; mensajes de auth unificados |
| **Injection** | `sanitizer.py` (SQLi, XSS, path traversal); validación Pydantic en schemas |
| **Rate limiting** | Global + límite más estricto en `/api/auth/login` y `/api/auth/register` |
| **Idempotencia** | Header `Idempotency-Key` en POST/PUT/PATCH (TTL configurable) |
| **Errores** | Respuestas 500 genéricas (`INTERNAL_ERROR_DETAIL`); sin `str(e)` en routers |
| **CORS** | Orígenes desde `CORS_ORIGINS` en `.env`; métodos y cabeceras acotados |
| **Carrito** | Validación de stock al actualizar cantidad (`400` si excede inventario) |
| **Pagos** | Pago en efectivo sin tarjeta; IDOR bloqueado en GET de pagos |

Copia [`.env.example`](.env.example) a `.env` y define `SECRET_KEY` antes de producción.

---

## Documentación adicional

| Documento | Contenido |
|-----------|-----------|
| [`docs/api_documentation.md`](docs/api_documentation.md) | Endpoints, cuerpos de petición, ejemplos `curl` y códigos HTTP |
| [`docs/user_manual.md`](docs/user_manual.md) | Instalación, roles, módulos y troubleshooting |
| [`docs/testing_document.md`](docs/testing_document.md) | Estrategia EP/BVA, vectores de ataque y escenarios de integración |
| [`backend/README.md`](backend/README.md) | Arquitectura en capas del backend |
| [`frontend/README.md`](frontend/README.md) | Estructura de componentes y convenciones React |
| [`tests/README.md`](tests/README.md) | Organización de la suite pytest |

---

## Créditos

Proyecto **Guerra de Testers** — plataforma educativa de ingeniería de software con énfasis en APIs de calidad, pruebas sistemáticas y documentación técnica completa.
