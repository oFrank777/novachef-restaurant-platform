# Restaurante Delivery API — Manual de Usuario

## Índice de Contenidos

1. [Visión General del Sistema](#vision-general-del-sistema)
2. [Guía de Instalación Rápida](#guia-de-instalacion-rapida)
3. [Guía de Inicio Rápido (Quickstart)](#guia-de-inicio-rapido-quickstart)
4. [Roles y Permisos](#roles-y-permisos)
5. [Guía de los Módulos](#guia-de-los-modulos)
6. [Referencia de Entradas Válidas](#referencia-de-entradas-validas)
7. [Resolución de Problemas Comunes (Troubleshooting)](#resolucion-de-problemas-comunes-troubleshooting)

---

## Visión General del Sistema

La **Restaurante Delivery API** es una aplicación web full-stack que permite a los restaurantes gestionar su menú, procesar pedidos de clientes, organizar las entregas, aceptar pagos y rastrear el inventario—todo mediante una interfaz limpia y orientada a roles.

### Funcionalidades Principales

- **Control de Acceso Basado en Roles (RBAC)**: Distingue los permisos entre `admin`, `cajero`, `delivery` y `cliente`.
- **Máquina de Estados de Pedidos Estricta**: Garantiza que los pedidos pasen de estado de forma lógica (ej. de "Pendiente" a "Preparando", en vez de "Entregado" repentinamente).
- **Gestión de Inventario en Tiempo Real**: Evita que se pidan platos que no están en stock.
- **Asignación de Conductores y Entregas**: Calcula costos y tiempo de entrega según la distancia para cada pedido.

---

## Guía de Instalación Rápida

Para iniciar el sistema de pruebas en tu entorno local, sigue estos pasos:

### Paso 1: Clonar el Repositorio

Si no lo has hecho, clona el proyecto y ve a su carpeta principal.

### Paso 2: Crear el Entorno Virtual (Recomendado)

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias del Backend

```bash
pip install -r backend/requirements.txt
```

### Paso 4: Configurar Variables de Entorno

Puedes configurar el sistema mediante variables de entorno (o usar los valores por defecto).

| Variable | Por Defecto | Descripción |
|----------|-------------|-------------|
| `JWT_SECRET` | "super_secret_key" | Llave usada para firmar los tokens JWT. CÁMBIALO en producción. |
| `DATABASE_URL` | "sqlite:///./restaurant.db" | Cadena de conexión para SQLAlchemy. |

### Paso 5: Inicializar la Base de Datos

La base de datos SQLite se crea automáticamente, genera las tablas requeridas e inyecta unos datos iniciales (semilla/seed) justo en el momento en el que arrancas el servidor del backend por primera vez. No es necesario ejecutar ningún script de base de datos manual.

**Credenciales Iniciales (Seed Data):**
Al clonar y arrancar el proyecto por primera vez, podrás ingresar inmediatamente al sistema usando las siguientes cuentas por defecto (según el rol que desees probar):

- **Administrador:** `admin` / `Admin123`
- **Cliente:** `cliente1` / `Cliente123`
- **Cajero:** `cajero1` / `Cajero123`
- **Repartidor (Delivery):** `delivery1` / `Delivery123`

### Paso 6: Arrancar el Servidor Backend

```bash
# Navega a la carpeta principal
set PYTHONPATH=.
# Arrancar Uvicorn en el puerto 8000
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Guía de Inicio Rápido (Quickstart)

A continuación, un flujo rápido de un cliente simulado utilizando la herramienta `curl`. 

### 1. Registrar un Cliente
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "cliente1", "email": "c1@test.com", "password": "PasswordSegura1", "role": "cliente"}'
```

### 2. Iniciar Sesión (Login)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "cliente1", "password": "PasswordSegura1"}'
```
*Copia el token JWT que devuelve ("access_token") para usarlo en el siguiente paso.*

### 3. Ver el Menú del Restaurante
```bash
curl http://localhost:8000/api/menu/
```

### 4. Añadir Artículo al Carrito (Reemplazar `<token>`)
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 1, "quantity": 2}'
```

### 5. Finalizar Compra y Crear el Pedido
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"delivery_address": "Mi Casa 123", "notes": "Sin cebolla"}'
```

---

## Roles y Permisos

El sistema implementa 4 roles exclusivos de usuario. El control de acceso está asegurado para que nadie sobrepase sus límites.

| Recurso / Módulo | `admin` | `cajero` | `delivery` | `cliente` |
|------------------|---------|----------|------------|-----------|
| **Menú** | Crear, Editar, Eliminar | Solo lectura | Solo lectura | Solo lectura |
| **Inventario** | Leer, Modificar | Leer | Denegado | Denegado |
| **Carrito** | Solo propio | Solo propio | Solo propio | Solo propio |
| **Pedidos** | Ver todos, Modificar estado | Ver todos, Modificar estado | Ver detalles | Solo los propios, Crear pedido |
| **Pagos** | Ver todos, Procesar pago | Ver todos | Denegado | Solo los propios, Pagar pedido propio |
| **Entregas** | Crear, Asignar, Ver | Solo lectura | Modificar estado de las suyas, Ver propias | Denegado |
| **Reportes** | Ver todas las estadísticas | Denegado | Denegado | Denegado |

---

## Guía de los Módulos

### Pedidos (Orders)

El módulo de Pedidos es el centro del negocio. Su estado es muy controlado y sigue esta línea estricta de trabajo.

#### Flujo de Estados del Pedido

```
┌─────────┐    ┌────────────┐    ┌───────┐    ┌──────────┐    ┌─────────┐    ┌───────────┐
│ PENDIENTE  │───▶│ PREPARANDO │───▶│ LISTO │───▶│ RECOGIDO │───▶│ ENVIADO │───▶│ ENTREGADO │
└─────────┘    └────────────┘    └───────┘    └──────────┘    └─────────┘    └───────────┘
     │
     ▼
┌───────────┐
│ CANCELADO │
└───────────┘
```

**Transiciones Válidas (Permitidas):**
- `PENDIENTE` → `PREPARANDO`
- `PENDIENTE` → `CANCELADO`
- `PREPARANDO` → `LISTO`
- `PREPARANDO` → `CANCELADO`
- `LISTO` → `RECOGIDO` (Para pedidos con Delivery)
- `LISTO` → `ENTREGADO` (Para pedidos con Recojo en Local)
- `LISTO` → `CANCELADO`
- `RECOGIDO` → `ENVIADO`
- `ENVIADO` → `ENTREGADO`

**Transiciones Inválidas (Rebotarán un 400 Bad Request):**
- De `PENDIENTE` a `ENTREGADO` directo.
- Retroceder, por ejemplo de `PREPARANDO` hacia `PENDIENTE`.
- Salir de un estado Terminal (Una vez que está `ENTREGADO` o `CANCELADO`, no hay marcha atrás).

#### Modificar el Estado de un Pedido (Para Administradores o Cajeros)

```bash
curl -X PATCH http://localhost:8000/api/orders/{id}/status \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "PREPARANDO"}'
```

---

### Entregas (Delivery)

Los administradores asocian una "Entrega" con una Orden creada y se la asignan a un conductor. Se calcula un costo basándose en un costo base más el número de Kilómetros.

#### Flujo de Estados de Entrega
Los estados permitidos son: `ASIGNADO`, `RECOGIDO`, `EN_TRANSITO`, `ENTREGADO`.

#### Para crear una Entrega y Asignar Chofer
```bash
curl -X POST http://localhost:8000/api/delivery/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "driver_id": 2,
    "address": "Calle Principal 123",
    "distance_km": 4.5
  }'
```

---

### Inventario (Inventory)

Evita que los clientes compren lo que no existe restando automáticamente los ingredientes cuando una Orden es colocada.

#### Revisar Artículos con Poco Stock

```bash
curl http://localhost:8000/api/inventory/low-stock \
  -H "Authorization: Bearer <admin_token>"
```

---

### Reportes (Reports)

Este módulo provee métricas clave para que los administradores tomen decisiones de negocio.

#### Ver Resumen de Ventas

```bash
curl http://localhost:8000/api/reports/sales \
  -H "Authorization: Bearer <admin_token>"
```

#### Ver Estado de Inventario en un Vistazo

```bash
curl http://localhost:8000/api/reports/inventory \
  -H "Authorization: Bearer <admin_token>"
```

#### Ver Los 20 Artículos Más Populares

```bash
curl http://localhost:8000/api/reports/popular \
  -H "Authorization: Bearer <admin_token>"
```

---

## Referencia de Entradas Válidas

Para evitar errores de validación de FastAPI (`422 Unprocessable Entity`), revisa este cuadro:

| Campo | Mínimo | Máximo | Reglas |
|-------|--------|--------|--------|
| `username` | 3 | 30 | Solo texto alfanumérico y guion bajo |
| `password` | 8 | 20 | Al menos 1 mayúscula y 1 número obligatorio |
| `menu.name` | 3 | 50 | Cualquier carácter |
| `menu.price` | 0.01 | 999.99 | Mayor que cero estricto |
| `cart.quantity`| 1 | 99 | Mayor que cero estricto |
| `payment.amount`| 0.01 | 5000.00| Debe coincidir exactamente con el valor del pedido |
| `card_number` | 16 | 16 | Solo dígitos (Ej. "4111111111111111") |
| `cvv` | 3 | 3 | Solo 3 dígitos exactos |
| `distance_km` | 0.5 | 20.0 | Kilómetros de distancia (máximo 20 km permitidos) |

---

## Rutas Complejas de la API (Chuleta/Cheat Sheet)

### Menú y Carrito
| Verbo | Ruta | Requiere Autenticación? | Uso principal |
|-------|------|-------------------------|---------------|
| GET | `/api/menu/` | No | Ver todo el menú |
| POST | `/api/menu/` | Sí (Admin) | Crear nuevo plato |
| GET | `/api/cart/` | Sí | Ver el propio carrito |
| POST | `/api/cart/` | Sí | Añadir al carrito |

### Pedidos, Pagos y Entregas
| Verbo | Ruta | Requiere Autenticación? | Uso principal |
|-------|------|-------------------------|---------------|
| GET | `/api/orders/{id}` | Sí | Detalle del pedido |
| POST | `/api/orders/` | Sí | Crear pedido desde carrito |
| PATCH | `/api/orders/{id}/status` | Admin / Cajero | Modificar estado de pedido |
| GET | `/api/delivery/` | Admin / Delivery | Listar todas las entregas |
| GET | `/api/delivery/{id}` | Admin / Delivery | Detalle de la entrega |
| GET | `/api/delivery/order/{id}` | Admin / Delivery | Obtener entrega por N° pedido |
| POST | `/api/delivery/` | Admin | Crear entrega |
| PATCH | `/api/delivery/{id}/status` | Admin / Delivery | Cambiar estado de entrega |
| GET | `/api/payments/` | Admin / Cajero | Listar todos los pagos |
| GET | `/api/payments/{id}` | Admin / Cajero | Detalle de pago individual |
| GET | `/api/payments/order/{id}` | Admin / Cajero | Obtener pago por N° de pedido |
| POST | `/api/payments/` | Sí | Pagar la orden (Simulado) |
| GET | `/api/inventory/` | Admin | Listado general de stock |
| GET | `/api/inventory/low-stock` | Admin | Alertas de stock bajo |
| PUT | `/api/inventory/{id}` | Admin | Sumar/Restar al inventario manual |

---

## Resolución de Problemas Comunes (Troubleshooting)

### Posibles Fallos

#### "ModuleNotFoundError: No module named 'backend'"

**Solución:** Asegúrate de estar ejecutando los comandos desde el directorio principal del proyecto y que tu entorno virtual Python esté activo. Adicionalmente, verifica si te falta exportar tu variable de ruta Python:

```bash
# Si estás en Windows:
set PYTHONPATH=.   

# Si estás en Linux / macOS:
export PYTHONPATH=. 
```

#### Recibes error "401 Unauthorized" en todas las peticiones

**Solución:** Tu Token JWT (`access_token`) puede haber caducado, o estás enviando el formato erróneo en Postman/cURL. Asegúrate de pasar en el Header HTTP la palabra exacta `Bearer` seguida de tu token.
```
Authorization: Bearer eyJhbGciO...
```

#### Recibes error "400 Bad Request" (Transición no válida)

**Solución:** Estás intentando saltarte pasos. Revisa el diagrama "Flujo de Estados del Pedido" y haz el salto de estado en orden. No puedes poner `ENTREGADO` si aún está `PENDIENTE`.

#### Recibes error "422 Unprocessable Entity" 

**Solución:** La información que enviaste tiene mala forma (Ej: Ingresaste `precio: "abc"`, en vez de un número real). Revisa la tabla de *Entradas Válidas* de este documento.
