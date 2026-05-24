# Restaurante Delivery API — Documentación de la API

## URL Base

```
http://localhost:8000
```

## Autenticación

Todos los endpoints protegidos requieren un token JWT en el encabezado `Authorization`:

```
Authorization: Bearer <token>
```

Puedes obtener un token llamando al endpoint `/api/auth/login`.

---

## Formato de Respuesta de Error

Todas las respuestas de error siguen esta estructura JSON:

```json
{
  "detail": "Mensaje de error que describe lo que salió mal"
}
```

### Códigos de Estado HTTP Comunes

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | Éxito (OK) | La solicitud se completó correctamente. |
| 201 | Creado (Created) | El recurso fue creado exitosamente. |
| 400 | Solicitud Incorrecta (Bad Request) | Error en la lógica de negocio o formato inválido. |
| 401 | No Autorizado (Unauthorized) | Falta el token o es inválido. |
| 403 | Prohibido (Forbidden) | Permisos insuficientes para el rol actual. |
| 404 | No Encontrado (Not Found) | El recurso solicitado no existe. |
| 409 | Conflicto (Conflict) | Intento de crear un recurso duplicado. |
| 422 | Entidad No Procesable (Unprocessable Entity) | Error de validación de datos (ej. faltan campos). |
| 500 | Error Interno (Internal Server Error) | Fallo inesperado en el servidor. |

---

## Endpoints

### 1. Autenticación (`/api/auth`)

#### 1.1 Registrar Usuario

```
POST /api/auth/register
```

**Autenticación:** Ninguna

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `username` | string | Sí | 3-30 caracteres, alfanumérico + guion bajo |
| `email` | string | Sí | Formato de correo electrónico válido |
| `password` | string | Sí | 8-20 caracteres, debe contener mayúscula + número |
| `role` | string | Sí | Valores permitidos: `admin`, `cliente`, `cajero`, `delivery` |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_perez",
    "email": "juan@example.com",
    "password": "PasswordSegura1",
    "role": "cliente"
  }'
```

**Respuesta (200):**

```json
{
  "id": 1,
  "username": "juan_perez",
  "email": "juan@example.com",
  "role": "cliente"
}
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 400/409 | El nombre de usuario ya existe |
| 422 | Error de validación (valores de campo inválidos) |

---

#### 1.2 Iniciar Sesión (Login)

```
POST /api/auth/login
```

**Autenticación:** Ninguna

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `username` | string | Sí |
| `password` | string | Sí |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_perez",
    "password": "PasswordSegura1"
  }'
```

**Respuesta (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 401 | Credenciales inválidas |

---

#### 1.3 Obtener Usuario Actual

```
GET /api/auth/me
```

**Autenticación:** Requerida (cualquier rol)

**Ejemplo de Petición:**

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

**Respuesta (200):**

```json
{
  "id": 1,
  "username": "juan_perez",
  "email": "juan@example.com",
  "role": "cliente"
}
```

---

### 2. Menú (`/api/menu`)

#### 2.1 Listar Artículos del Menú

```
GET /api/menu/
```

**Autenticación:** Ninguna (público)

**Ejemplo de Petición:**

```bash
curl http://localhost:8000/api/menu/
```

**Respuesta (200):**

```json
[
  {
    "id": 1,
    "name": "Pizza Margherita",
    "description": "Pizza clásica con mozzarella fresca y albahaca",
    "price": 12.99,
    "category": "Pizzas",
    "available": true
  }
]
```

---

#### 2.2 Obtener un Artículo Específico del Menú

```
GET /api/menu/{id}
```

**Autenticación:** Ninguna (público)

**Ejemplo de Petición:**

```bash
curl http://localhost:8000/api/menu/1
```

**Respuesta (200):**

```json
{
  "id": 1,
  "name": "Pizza Margherita",
  "description": "Pizza clásica con mozzarella fresca y albahaca",
  "price": 12.99,
  "category": "Pizzas",
  "available": true
}
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 404 | Artículo del menú no encontrado |

---

#### 2.3 Crear Artículo del Menú

```
POST /api/menu/
```

**Autenticación:** Requerida (solo admin)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `name` | string | Sí | 3-50 caracteres |
| `description` | string | No | Texto libre |
| `price` | float | Sí | 0.01-999.99 |
| `category` | string | No | Texto libre |
| `available` | boolean | No | Por defecto: true |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/menu/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pizza Margherita",
    "description": "Pizza clásica con mozzarella fresca y albahaca",
    "price": 12.99,
    "category": "Pizzas",
    "available": true
  }'
```

---

#### 2.4 Actualizar Artículo del Menú

```
PUT /api/menu/{id}
```

**Autenticación:** Requerida (solo admin)

**Cuerpo de la Petición:** Igual que Crear (todos los campos son opcionales para actualización parcial).

**Ejemplo de Petición:**

```bash
curl -X PUT http://localhost:8000/api/menu/1 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"price": 14.99}'
```

---

#### 2.5 Eliminar Artículo del Menú

```
DELETE /api/menu/{id}
```

**Autenticación:** Requerida (solo admin)

**Ejemplo de Petición:**

```bash
curl -X DELETE http://localhost:8000/api/menu/1 \
  -H "Authorization: Bearer <admin_token>"
```

**Respuesta (200):**

```json
{
  "detail": "Artículo del menú eliminado exitosamente"
}
```

---

### 3. Carrito de Compras (`/api/cart`)

#### 3.1 Ver Carrito

```
GET /api/cart/
```

**Autenticación:** Requerida

**Respuesta (200):**

```json
[
  {
    "id": 1,
    "menu_item_id": 1,
    "menu_item_name": "Pizza Margherita",
    "quantity": 2,
    "unit_price": 12.99,
    "subtotal": 25.98
  }
]
```

---

#### 3.2 Añadir Artículo al Carrito

```
POST /api/cart/
```

**Autenticación:** Requerida

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `menu_item_id` | integer | Sí | Debe existir en el menú |
| `quantity` | integer | Sí | 1-99 |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 1, "quantity": 2}'
```

---

#### 3.3 Actualizar Cantidad de Artículo en el Carrito

```
PUT /api/cart/{id}
```

**Autenticación:** Requerida

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `quantity` | integer | Sí | 1-99 |

---

#### 3.4 Eliminar Artículo del Carrito

```
DELETE /api/cart/{id}
```

**Autenticación:** Requerida

---

#### 3.5 Vaciar Carrito Completo

```
DELETE /api/cart/
```

**Autenticación:** Requerida

---

### 4. Pedidos (`/api/orders`)

#### 4.1 Listar Pedidos

```
GET /api/orders/
```

**Autenticación:** Requerida

- **Admin/Cajero**: Ver todos los pedidos.
- **Cliente**: Ver solo sus propios pedidos.
- **Entrega (Delivery)**: Ver pedidos asignados para entregar.

---

#### 4.2 Obtener Detalle de Pedido

```
GET /api/orders/{id}
```

**Autenticación:** Requerida

**Respuesta (200):**

```json
{
  "id": 1,
  "user_id": 2,
  "status": "PENDIENTE",
  "total": 25.98,
  "delivery_address": "Calle Principal 123",
  "items": [
    {
      "menu_item_id": 1,
      "menu_item_name": "Pizza Margherita",
      "quantity": 2,
      "unit_price": 12.99,
      "subtotal": 25.98
    }
  ],
  "created_at": "2026-05-23T18:00:00"
}
```

---

#### 4.3 Crear Pedido

```
POST /api/orders/
```

**Autenticación:** Requerida

Crea un pedido a partir de los artículos actuales en el carrito. El carrito no debe estar vacío.

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `delivery_address` | string | Sí | 5-200 caracteres |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"delivery_address": "Calle Principal 123, Depto 4B"}'
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 400 | El carrito está vacío o supera el monto máximo permitido ($5000.00) |

---

#### 4.4 Actualizar Estado de Pedido

```
PATCH /api/orders/{id}/status
```

**Autenticación:** Requerida (admin o cajero)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `status` | string | Sí | Siguiente estado válido (ver máquina de estados) |

**Valores de Estado Válidos:** `PENDIENTE`, `PREPARANDO`, `LISTO`, `RECOGIDO`, `ENVIADO`, `ENTREGADO`, `CANCELADO`

**Transiciones Válidas:**

| Estado Actual | Siguiente Permitido |
|---------------|---------------------|
| PENDIENTE | PREPARANDO, CANCELADO |
| PREPARANDO | LISTO, CANCELADO |
| LISTO | RECOGIDO, ENTREGADO, CANCELADO |
| RECOGIDO | ENVIADO |
| ENVIADO | ENTREGADO |
| ENTREGADO | (ninguno — terminal) |
| CANCELADO | (ninguno — terminal) |

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 400 | Transición de estado inválida |
| 403 | Permisos insuficientes |
| 404 | Pedido no encontrado |

---

### 5. Entregas (`/api/delivery`)

#### 5.1 Listar Entregas

```
GET /api/delivery/
```

**Autenticación:** Requerida (admin o delivery)

Devuelve la lista de entregas. Si el usuario es de rol `delivery`, solo verá las entregas asignadas a él.

---

#### 5.2 Obtener Detalle de Entrega

```
GET /api/delivery/{id}
```

**Autenticación:** Requerida (admin o delivery)

**Respuesta (200):**

```json
{
  "id": 1,
  "order_id": 1,
  "driver_id": 5,
  "address": "Calle Principal 123, Depto 4B",
  "distance_km": 5.5,
  "delivery_cost": 10.25,
  "status": "EN_TRANSITO",
  "created_at": "2026-05-23T18:00:00"
}
```

---

#### 5.3 Obtener Entrega por Pedido

```
GET /api/delivery/order/{order_id}
```

**Autenticación:** Requerida (admin o delivery)

---

#### 5.4 Crear Entrega

```
POST /api/delivery/
```

**Autenticación:** Requerida (admin)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `order_id` | integer | Sí | Debe existir |
| `driver_id` | integer | No | Usuario con rol de delivery |
| `address` | string | Sí | 5-200 caracteres |
| `distance_km` | float | Sí | 0.5-20.0 |

**Cálculo de Costo:**

```
delivery_cost = 2.0 + (distance_km × 1.5)
```

---

#### 5.5 Actualizar Estado de Entrega

```
PATCH /api/delivery/{id}/status
```

**Autenticación:** Requerida (admin o delivery)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `status` | string | Sí |
| `driver_id` | integer | No |

**Valores de Estado Válidos:** `ASIGNADO`, `RECOGIDO`, `EN_TRANSITO`, `ENTREGADO`

---

### 6. Pagos (`/api/payments`)

#### 6.1 Listar Pagos

```
GET /api/payments/
```

**Autenticación:** Requerida (admin o cajero)

---

#### 6.2 Obtener Detalle de Pago

```
GET /api/payments/{id}
```

**Autenticación:** Requerida (admin o cajero)

**Respuesta (200):**

```json
{
  "id": 1,
  "order_id": 1,
  "amount": 25.98,
  "card_last_four": "1111",
  "card_holder": "Juan Perez",
  "status": "COMPLETED",
  "created_at": "2026-05-23T18:00:00"
}
```

> **Nota de Seguridad:** Solo se almacenan y devuelven los últimos 4 dígitos del número de la tarjeta.

---

#### 6.3 Obtener Pago por Pedido

```
GET /api/payments/order/{order_id}
```

**Autenticación:** Requerida (admin o cajero)

---

#### 6.4 Procesar Pago

```
POST /api/payments/
```

**Autenticación:** Requerida

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `order_id` | integer | Sí | Debe existir, sin pago previo |
| `amount` | float | Sí | 0.01-5000.00 (Debe coincidir con el total del pedido) |
| `card_number` | string | Sí | 16 dígitos |
| `card_holder` | string | Sí | Cadena no vacía |
| `expiry_date` | string | Sí | Formato: MM/YY |
| `cvv` | string | Sí | 3 dígitos |

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:8000/api/payments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 25.98,
    "card_number": "4111111111111111",
    "card_holder": "Juan Perez",
    "expiry_date": "12/28",
    "cvv": "123"
  }'
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 400/409 | El pago ya existe para este pedido |
| 404 | Pedido no encontrado |
| 422 | Datos de tarjeta inválidos |

---

### 7. Inventario (`/api/inventory`)

#### 7.1 Listar Inventario

```
GET /api/inventory/
```

**Autenticación:** Requerida (admin)

**Respuesta (200):**

```json
[
  {
    "id": 1,
    "menu_item_id": 1,
    "menu_item_name": "Pizza Margherita",
    "stock": 50,
    "min_stock": 10
  }
]
```

---

#### 7.2 Obtener Artículos con Stock Bajo

```
GET /api/inventory/low-stock
```

**Autenticación:** Requerida (admin)

Devuelve los artículos donde `stock <= min_stock`.

---

#### 7.3 Actualizar Stock

```
PUT /api/inventory/{id}
```

**Autenticación:** Requerida (admin)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `stock` | integer | Sí | 0-9999 |
| `min_stock` | integer | No | 0-999 |

**Ejemplo de Petición:**

```bash
curl -X PUT http://localhost:8000/api/inventory/1 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"stock": 50, "min_stock": 10}'
```

**Respuestas de Error:**

| Código | Condición |
|--------|-----------|
| 403 | Usuario no administrador |
| 404 | Artículo de inventario no encontrado |
| 422 | Valores de stock inválidos |

---

#### 7.4 Crear Artículo de Inventario

```
POST /api/inventory/
```

**Autenticación:** Requerida (admin)

**Cuerpo de la Petición:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `menu_item_id` | integer | Sí | Debe existir en el menú |
| `stock` | integer | Sí | 0-9999 |
| `min_stock` | integer | No | Por defecto: 10 |

---

#### 7.5 Obtener un Solo Artículo de Inventario

```
GET /api/inventory/{id}
```

**Autenticación:** Requerida (admin o cajero)

---

### 8. Reportes (`/api/reports`)

El módulo de reportes proporciona análisis detallados sobre las ventas, el inventario y el rendimiento del restaurante.

#### 8.1 Reporte de Ventas (Sales Report)

```
GET /api/reports/sales
```

**Autenticación:** Requerida (admin)

**Respuesta:**
Devuelve el total de pedidos realizados, los ingresos totales generados y un desglose detallado de los ingresos agrupados por el estado de cada pedido.

---

#### 8.2 Reporte de Inventario (Inventory Report)

```
GET /api/reports/inventory
```

**Autenticación:** Requerida (admin)

**Respuesta:**
Devuelve el número total de artículos rastreados en el inventario, la suma total de existencias actuales y un recuento de cuántos artículos se encuentran con nivel de stock bajo (por debajo del límite mínimo configurado).

---

#### 8.3 Reporte de Artículos Populares (Popular Items Report)

```
GET /api/reports/popular
```

**Autenticación:** Requerida (admin)

**Respuesta:**
Devuelve una lista con el Top 20 de los artículos más populares basándose en la cantidad total de veces que han sido ordenados, incluyendo la cantidad total vendida y los ingresos generados por cada uno.
