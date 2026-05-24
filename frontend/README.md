# Documentación del Frontend

Este directorio aloja la aplicación cliente (interfaz de usuario) desarrollada con **React** y construida empleando la herramienta de empaquetado **Vite** para ofrecer una experiencia de desarrollo veloz y eficiente.

## Arquitectura y Estructura

El código principal reside dentro de la carpeta `src/`. El proyecto sigue una organización modular basada en características y funcionalidades para mantener el código desacoplado y mantenible.

### 1. Componentes (`src/components/`)
Contiene los elementos visuales de React. Está subdividido para promover la reutilización:
- **`common/`**: Componentes atómicos e independientes como botones, campos de entrada, insignias (badges) y elementos visuales genéricos que se utilizan a lo largo de toda la aplicación.
- **`Layout/`**: Componentes estructurales que definen el esqueleto de la aplicación, como la barra de navegación (Navbar), la protección de rutas (`ProtectedRoute.jsx`) y el contenedor principal de diseño (`Layout.jsx`).

### 2. Vistas / Páginas (`src/pages/`)
Representan pantallas completas de la aplicación (por ejemplo, `OrdersPage.jsx`, `DeliveryPage.jsx`, `LoginPage.jsx`). Estas vistas ensamblan múltiples componentes comunes y están directamente enlazadas al enrutador principal (React Router) en `App.jsx`.

### 3. Contexto Global (`src/context/`)
Gestiona el estado global de la aplicación empleando React Context. Aquí se ubican administradores de estado crítico como la sesión del usuario (`AuthContext.jsx`) y el manejo de los productos en la canasta (`CartContext.jsx`). 

### 4. Cliente de API (`src/api/`)
Centraliza toda la comunicación asíncrona con el servidor Backend. El archivo `client.js` implementa un cliente **Axios** preconfigurado (interceptores) que automáticamente adjunta los tokens de autorización (JWT) a cada solicitud y maneja globalmente los errores de red y de validación devueltos por el servidor.

### 5. Estilos (`src/styles/`)
Contiene las hojas de estilo en cascada (CSS). La aplicación utiliza una metodología de diseño centralizada donde los tokens de diseño (colores, sombras, radios de borde) y las clases utilitarias residen en `global.css`, asegurando consistencia visual en todo el ecosistema de componentes.

### 6. Constantes compartidas (`src/constants/`)
Centraliza valores que deben coincidir con el backend:
- **`orderStatus.js`**: estados (`PENDIENTE`, `PREPARANDO`, …, `CANCELADO`), etiquetas en español, colores, función `getNextStatuses(order, role)` e `isPickupOrder(order)` para distinguir mostrador vs domicilio.

> **Importante:** al cancelar un pedido, la UI debe enviar `status: "CANCELADO"`. Usar `CANCELLED` provoca error **422** en la API.

## Pantallas y flujo por rol

La navegación se define en `src/components/Layout/Layout.jsx` (`navItems`). Resumen operativo:

| Rol | Rutas principales | Función en el negocio |
|-----|-------------------|------------------------|
| **admin** | Panel, Menú, Carrito, Pedidos, Pagos, Inventario, Entregas, Reportes | Supervisión y control total |
| **cajero** | Panel, Menú, Carrito, Pedidos, Pagos | Cocina, cancelaciones, entrega en mostrador |
| **cliente** | Panel, Menú, Carrito, Pedidos | Compra y seguimiento de pedidos propios |
| **delivery** | Panel, Pedidos (consulta), Entregas | Ruta de entrega a domicilio |

### Páginas críticas del flujo

| Archivo | Descripción |
|---------|-------------|
| `OrdersPage.jsx` | Cola de pedidos; botones de transición y cancelación (`CANCELADO`) según rol |
| `DeliveryPage.jsx` | Entregas a domicilio; avance `RECOGIDO` → `ENVIADO` → `ENTREGADO`; asignación de repartidor vía API `/api/delivery` |
| `DashboardPage.jsx` | Resumen adaptado: cajero (cola cocina), delivery (listos/en ruta), cliente (activos/gasto) |
| `CartPage.jsx` | Checkout; `delivery_address` o «Recogida en local» define el tipo de pedido |
| `PaymentsPage.jsx` | Transacciones (admin/cajero); excluye pedidos `CANCELADO` |

## Convenciones de Desarrollo

- **Comunicación Eficiente:** Todos los componentes se apoyan fuertemente en el bus de eventos (`src/utils/eventEmitter.js`) para desplegar notificaciones (Toasts) globales de error o éxito sin tener que propagar propiedades.
- **Sin Estado Innecesario:** Los componentes comunes (dentro de `common/`) se mantienen como componentes de presentación siempre que es posible, dejando el manejo de datos y llamadas de red a los componentes ubicados en `pages/`.

## Ejecución de la Aplicación

Para desplegar la aplicación en entorno de desarrollo, con recarga en caliente (HMR), asegúrese de tener resueltas las dependencias (`npm install`) y ejecute:

```bash
npm run dev
```

El servidor local se levantará, por defecto, en el puerto indicado en la consola (usualmente `http://localhost:5173`).

El proxy de Vite (`vite.config.js`) reenvía `/api` → `http://localhost:8000`; el backend debe estar en ejecución para probar flujos de cajero y repartidor.

### Prueba rápida del flujo completo (UI)

1. Login como `cliente1` → pedido con dirección de entrega.
2. Login como `cajero1` → **Pedidos** → Preparando → Listo.
3. Login como `delivery1` → **Entregas** → Recogido → En camino → Entregado.

Usuarios demo documentados en el [`README.md`](../README.md) de la raíz del repositorio.

---

## Seguridad en el cliente

| Elemento | Descripción |
|----------|-------------|
| `src/api/client.js` | Mensajes de error seguros por código HTTP; evento `auth:logout` en 401 |
| `src/utils/idempotency.js` | Genera `Idempotency-Key` para evitar doble envío de pedidos |
| `src/constants/orderStatus.js` | Estados alineados con API (`CANCELADO`, no `CANCELLED`) |
| `App.jsx` + `ProtectedRoute` | Rutas con `roles` explícitos por pantalla |
| `RegisterPage.jsx` | Sin selector de rol admin/cajero/delivery |
| `AuthContext.jsx` | Rollback de sesión si falla `/auth/me` tras login |
| Formularios | Anti doble-submit en carrito, menú, inventario y pedidos |

### Cabecera Idempotency-Key

`CartPage.jsx` envía `Idempotency-Key` al crear pedidos (`POST /api/orders/`).
