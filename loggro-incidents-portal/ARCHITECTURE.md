# ARCHITECTURE.md — Portal Interno de Incidencias Loggro

## Índice

1. [Visión General](#1-visión-general)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Flujo de Datos](#3-flujo-de-datos)
4. [Seguridad](#4-seguridad)
5. [Integración con Intercom](#5-integración-con-intercom)
6. [Base de Datos](#6-base-de-datos)
7. [Configuración Dinámica](#7-configuración-dinámica)
8. [Observabilidad y Logging](#8-observabilidad-y-logging)
9. [Despliegue](#9-despliegue)
10. [Decisiones de Diseño](#10-decisiones-de-diseño)
11. [Roadmap SSO y Extensiones Futuras](#11-roadmap-sso-y-extensiones-futuras)

---

## 1. Visión General

El **Portal Interno de Incidencias Loggro** es una aplicación web independiente que permite a los equipos internos de Loggro (Comercial, Implementaciones, Customer Success, Producto, etc.) registrar tickets de soporte directamente en Intercom **sin crear conversaciones de chat ni interactuar con el Messenger de FIN**.

### Principios de diseño

| Principio | Implementación |
|---|---|
| Independencia total | Subdirectorio propio, sin importar ni modificar ningún archivo de FIN Architect |
| Config-as-data | Todos los productos, tipos, prioridades y campos viven en SQLite, no en el código |
| Seguridad por capas | Validación de dominio, rate limiting, CSRF, Helmet, CORS restrictivo |
| SSO-ready | Capa de autenticación desacoplada, preparada para JWT de Entra ID o Google Workspace |
| Observabilidad | Logging estructurado JSON (Winston), audit trail completo en SQLite |
| Zero-hardcode | Ningún ID de Intercom ni credencial en el código fuente |

### Stack tecnológico

```
Frontend:  React 18 + Vite + TypeScript + Tailwind CSS + React Router v6
Backend:   Node.js 20 + Express 4 + TypeScript + ts-node
Database:  SQLite 3 (better-sqlite3) — sin servidor, archivo local
Logging:   Winston (JSON estructurado)
Seguridad: Helmet, express-rate-limit, tokens CSRF custom, multer
```

---

## 2. Estructura del Proyecto

```
loggro-incidents-portal/
│
├── ARCHITECTURE.md            ← Este documento
├── README.md                  ← Guía de instalación y uso
├── package.json               ← Scripts raíz: dev, build, start
├── .gitignore
│
├── backend/
│   ├── .env.example           ← Variables de entorno documentadas
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── app.ts             ← Express app (middlewares, routes)
│       ├── server.ts          ← Entry point (listen)
│       │
│       ├── config/
│       │   └── index.ts       ← Centraliza y valida todas las env vars
│       │
│       ├── database/
│       │   ├── connection.ts  ← Singleton de conexión SQLite
│       │   └── migrations.ts  ← Schema DDL + seed de configuración inicial
│       │
│       ├── middleware/
│       │   ├── domainAuth.ts  ← Valida que el email sea @loggro.com
│       │   ├── rateLimiter.ts ← express-rate-limit configurable
│       │   ├── csrfProtection.ts ← Token CSRF stateless (HMAC-SHA256)
│       │   └── requestLogger.ts  ← Log estructurado por request
│       │
│       ├── models/
│       │   ├── TicketHistory.ts ← CRUD del historial de tickets
│       │   └── PortalConfig.ts  ← CRUD de configuración dinámica
│       │
│       ├── routes/
│       │   ├── tickets.ts     ← POST /api/tickets
│       │   ├── config.ts      ← GET /api/config (público para el form)
│       │   └── admin.ts       ← CRUD /api/admin/* (protegido con API key)
│       │
│       ├── controllers/
│       │   ├── ticketController.ts  ← Orquesta creación de ticket
│       │   ├── configController.ts  ← Devuelve config al frontend
│       │   └── adminController.ts   ← CRUD de configuración y historial
│       │
│       ├── services/
│       │   ├── intercomService.ts   ← Toda la lógica de la API de Intercom
│       │   ├── configService.ts     ← Lectura/escritura de config dinámica
│       │   └── historyService.ts    ← Registro de auditoría
│       │
│       └── utils/
│           ├── logger.ts      ← Winston configurado (JSON + color en dev)
│           └── validators.ts  ← Validadores compartidos (email, archivo)
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src/
        ├── main.tsx
        ├── App.tsx            ← Router principal
        ├── types/
        │   └── index.ts       ← Tipos compartidos (PortalConfig, TicketForm, etc.)
        │
        ├── services/
        │   └── api.ts         ← Axios instance + todas las llamadas al backend
        │
        ├── hooks/
        │   ├── usePortalConfig.ts  ← Carga config dinámica del backend
        │   └── useTicketSubmit.ts  ← Lógica de envío del formulario
        │
        ├── components/
        │   ├── ui/            ← Componentes base reutilizables
        │   │   ├── Button.tsx
        │   │   ├── Input.tsx
        │   │   ├── Select.tsx
        │   │   ├── Textarea.tsx
        │   │   ├── Badge.tsx
        │   │   ├── Card.tsx
        │   │   ├── Spinner.tsx
        │   │   └── FileUpload.tsx
        │   │
        │   ├── form/          ← Componentes específicos del formulario
        │   │   ├── ProductSelector.tsx
        │   │   ├── DynamicField.tsx
        │   │   └── FormSection.tsx
        │   │
        │   └── layout/        ← Estructura de página
        │       ├── Header.tsx
        │       └── PageWrapper.tsx
        │
        └── pages/
            ├── IncidentForm.tsx   ← Formulario principal
            ├── Confirmation.tsx   ← Página de éxito post-envío
            └── Admin.tsx          ← Dashboard de administración
```

---

## 3. Flujo de Datos

### 3.1 Carga del formulario

```
Browser
  │── GET /api/config ──────────────────────────────────────────────────▶ Backend
  │                                                                           │
  │                    configService.getConfig()                              │
  │                           │                                               │
  │                    SQLite portal_config ───────────────────────────────▶ │
  │                                                                           │
  │◀── JSON: { products, requestTypes, priorities, teams } ───────────────── │
  │
  └── React renderiza formulario dinámico según config
```

### 3.2 Envío de un ticket

```
Browser
  │
  │ 1. Valida dominio @loggro.com (client-side, rápido)
  │ 2. Adjunta archivos (multipart/form-data)
  │ 3. Incluye header X-CSRF-Token
  │
  │── POST /api/tickets ────────────────────────────────────────────────▶ Backend
                                                                              │
                                          Middleware stack:                   │
                                          [1] rateLimiter (5 req/15min/IP)    │
                                          [2] csrfProtection (HMAC valida)    │
                                          [3] multer (archivos, max 10MB)     │
                                          [4] domainAuth (@loggro.com)        │
                                          [5] ticketController                │
                                                    │                         │
                                          ┌─────────┴──────────┐             │
                                          │                    │             │
                                   intercomService        historyService     │
                                          │                    │             │
                                    Intercom API          SQLite INSERT      │
                                    POST /tickets         ticket_history     │
                                          │                                  │
                                    { ticket.id,                             │
                                      ticket.url }                           │
                                          │                                  │
                                          └──────────── UPDATE status ───── │
                                                        (success/error)      │
                                                                             │
Browser ◀── { ticketId, ticketUrl, createdAt, product, priority } ───────── │
  │
  └── Redirect a /confirmation?id=...
```

### 3.3 Token CSRF

```
Browser carga el formulario
  │── GET /api/csrf-token ─────────────────────────────────────────────▶ Backend
  │◀── { csrfToken: "HMAC(secret, sessionId, timestamp)" } ──────────── │
  │
  └── Almacena token en memoria React (NO en localStorage)

Envío del formulario:
  └── Header: X-CSRF-Token: <token>
  └── Backend verifica HMAC antes de procesar
```

---

## 4. Seguridad

### 4.1 Validación de dominio corporativo

**Frontend (UX rápida):** Validación client-side en tiempo real sobre el campo email — solo visual, no es la barrera de seguridad.

**Backend (barrera real):** El middleware `domainAuth` extrae el email del body/form, verifica que termine en `@loggro.com` con regex estricta, y rechaza con HTTP 403 cualquier solicitud que no cumpla.

```typescript
// domainAuth.ts
const ALLOWED_DOMAIN = config.allowedEmailDomain; // '@loggro.com' desde .env
const emailRegex = /^[a-zA-Z0-9._%+-]+@loggro\.com$/i;
```

### 4.2 Rate Limiting

| Endpoint | Límite | Ventana | Acción al superar |
|---|---|---|---|
| POST /api/tickets | 5 requests | 15 minutos | 429 Too Many Requests |
| POST /api/tickets | 20 requests | 1 hora | 429 Too Many Requests |
| GET /api/config | 60 requests | 1 minuto | 429 Too Many Requests |
| /api/admin/* | 10 requests | 1 minuto | 429 Too Many Requests |

Los límites son configurables vía variables de entorno.

### 4.3 Protección CSRF

Token HMAC-SHA256 stateless: `HMAC(CSRF_SECRET, clientFingerprint + timestamp)`.
- El token expira en 1 hora.
- No requiere sesión ni cookies de estado.
- Compatible con arquitectura SSO futura.

### 4.4 Headers de seguridad (Helmet)

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000
Referrer-Policy: strict-origin-when-cross-origin
```

### 4.5 CORS

Solo acepta orígenes configurados en `CORS_ORIGIN` (env var). En producción debe ser el dominio exacto del frontend.

### 4.6 Validación de archivos

- Tamaño máximo: configurable (`MAX_FILE_SIZE_MB`, default 10MB).
- Tipos permitidos: `ALLOWED_FILE_TYPES` (env var, default: `image/jpeg,image/png,application/pdf,application/msword,...`).
- Validación de magic bytes (no confiar solo en la extensión).
- Máximo de archivos por envío: 5.

### 4.7 Admin Dashboard

Protegido con `ADMIN_API_KEY` (Bearer token en header). En producción, esta key debe rotarse regularmente. El endpoint admin **no está expuesto al público** — documentado para uso interno.

### 4.8 Preparación SSO

```typescript
// auth middleware (futuro)
interface AuthContext {
  userId: string;
  email: string;
  name: string;
  provider: 'loggro-sso' | 'entra-id' | 'google-workspace' | 'api-key';
  roles: string[];
}
```

El middleware de autenticación recibirá un JWT firmado por el IdP. El domainAuth actual se reemplazará por la verificación de claims del token. No se requieren cambios en controllers ni services.

---

## 5. Integración con Intercom

### 5.1 Flujo de creación de ticket

```
1. Backend recibe datos del formulario (validados)
2. intercomService.findOrCreateContact(email, name)
   ├── GET /contacts/search?query={email}
   └── POST /contacts  (si no existe)
3. intercomService.createTicket({
     ticket_type_id,    ← de la config del producto
     contacts: [{ id }],
     ticket_attributes: {
       _default_title_: "...",
       _default_description_: "...",
       ...camposCustom
     }
   })
4. Intercom ejecuta sus Assignment Rules automáticamente
5. Retorna { id, url }
```

### 5.2 Endpoints de Intercom utilizados

| Método | Endpoint | Propósito |
|---|---|---|
| GET | `/contacts/search` | Buscar contact por email |
| POST | `/contacts` | Crear contact si no existe |
| POST | `/tickets` | Crear ticket |

**Nota:** No se usa el Messenger SDK, no se crean conversations, no se envían mensajes al usuario final.

### 5.3 Configuración de ticket por producto

Cada producto en la config dinámica tiene su propio `intercomTicketTypeId`. El backend lee este ID de la config y lo usa en la llamada a Intercom. Las reglas de asignación de Intercom se disparan automáticamente basadas en el `ticket_type_id` y los atributos del ticket.

### 5.4 Manejo de errores de Intercom

```
Intercom API error → Log estructurado (Winston)
                   → Registro en ticket_history con status='error' y error_message
                   → Retorna 502 al frontend con mensaje amigable
                   → NO expone detalles internos de Intercom al browser
```

---

## 6. Base de Datos

### 6.1 Schema SQLite

```sql
-- Historial de auditoría
CREATE TABLE ticket_history (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
  requester_name      TEXT NOT NULL,
  requester_email     TEXT NOT NULL,
  company_name        TEXT,
  company_nit         TEXT,
  product             TEXT NOT NULL,
  request_type        TEXT NOT NULL,
  priority            TEXT NOT NULL,
  operational_impact  TEXT,
  description         TEXT NOT NULL,
  intercom_ticket_id  TEXT,
  intercom_ticket_url TEXT,
  status              TEXT NOT NULL DEFAULT 'pending',
  error_message       TEXT,
  ip_address          TEXT,
  user_agent          TEXT,
  response_time_ms    INTEGER
);

-- Configuración dinámica (key-value JSON)
CREATE TABLE portal_config (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  config_key   TEXT UNIQUE NOT NULL,
  config_value TEXT NOT NULL,   -- JSON serializado
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 Datos iniciales (seed)

Al arrancar por primera vez, `migrations.ts` inserta la configuración por defecto con los 6 productos de Loggro, tipos de solicitud, prioridades y un conjunto inicial de campos dinámicos. Esta configuración es editable desde el Admin Dashboard sin reiniciar el backend.

---

## 7. Configuración Dinámica

### 7.1 Estructura de configuración

```jsonc
// config_key: "portal_config"
{
  "products": [
    {
      "id": "erp-pymes",
      "name": "ERP-PYMES",
      "icon": "🏢",
      "active": true,
      "intercomTicketTypeId": "ENV:INTERCOM_TICKET_TYPE_ERP_PYMES",
      "dynamicFields": [
        {
          "id": "erp_module",
          "type": "select",
          "label": "Módulo afectado",
          "required": true,
          "options": ["Facturación", "Inventario", "Contabilidad", "Compras", "RRHH"]
        }
      ]
    }
    // ... otros productos
  ],
  "requestTypes": [
    { "id": "bug", "name": "Error / Bug", "active": true },
    { "id": "feature", "name": "Solicitud de mejora", "active": true },
    { "id": "support", "name": "Soporte operativo", "active": true }
  ],
  "priorities": [
    { "id": "critical", "name": "Crítica", "color": "red",    "slaHours": 4  },
    { "id": "high",     "name": "Alta",    "color": "orange", "slaHours": 8  },
    { "id": "medium",   "name": "Media",   "color": "yellow", "slaHours": 24 },
    { "id": "low",      "name": "Baja",    "color": "green",  "slaHours": 72 }
  ],
  "teams": [
    { "id": "comercial",        "name": "Comercial" },
    { "id": "implementaciones", "name": "Implementaciones" },
    { "id": "cs",               "name": "Customer Success" },
    { "id": "producto",         "name": "Producto" }
  ]
}
```

### 7.2 Admin API endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/admin/config` | Lee config completa |
| PUT | `/api/admin/config` | Reemplaza config completa |
| PATCH | `/api/admin/config/products` | Actualiza lista de productos |
| PATCH | `/api/admin/config/request-types` | Actualiza tipos de solicitud |
| PATCH | `/api/admin/config/priorities` | Actualiza prioridades |
| GET | `/api/admin/history` | Lista historial con filtros y paginación |
| GET | `/api/admin/history/:id` | Detalle de un registro |
| GET | `/api/admin/stats` | Estadísticas (tickets por producto, estado, etc.) |

---

## 8. Observabilidad y Logging

### 8.1 Niveles de log

```
ERROR  → Errores de Intercom API, errores inesperados, excepciones
WARN   → Rate limit activado, validaciones fallidas, archivos rechazados
INFO   → Ticket creado exitosamente, requests completados
DEBUG  → Payload enviado a Intercom, respuesta de Intercom, tiempos internos
```

### 8.2 Formato JSON estructurado (producción)

```json
{
  "timestamp": "2024-01-15T14:32:01.123Z",
  "level": "info",
  "message": "Ticket created successfully",
  "service": "loggro-incidents-portal",
  "requestId": "req-abc123",
  "ticketId": "123456",
  "intercomTicketId": "789",
  "product": "erp-pymes",
  "email": "usuario@loggro.com",
  "responseTimeMs": 342
}
```

En desarrollo: output legible con colores en la terminal.

### 8.3 Métricas capturadas

- Tiempo de respuesta de cada request
- Tiempo de respuesta de Intercom API
- Errores de Intercom (4xx, 5xx, timeout)
- Rate limit hits
- Intentos de email no-loggro.com bloqueados

---

## 9. Despliegue

### 9.1 Desarrollo local

```bash
# Desde loggro-incidents-portal/
npm run dev
# Levanta backend (puerto 3001) y frontend (puerto 5173) concurrentemente
```

### 9.2 Variables de entorno requeridas

```bash
# Intercom
INTERCOM_ACCESS_TOKEN=    # Token de acceso a la API de Intercom
INTERCOM_API_VERSION=2.11 # Versión de la API

# IDs de Ticket Types por producto (configurar en Intercom primero)
INTERCOM_TICKET_TYPE_ERP_PYMES=
INTERCOM_TICKET_TYPE_RESTOBAR=
INTERCOM_TICKET_TYPE_POS_TIENDA=
INTERCOM_TICKET_TYPE_NOMINA=
INTERCOM_TICKET_TYPE_ALOJAMIENTOS=
INTERCOM_TICKET_TYPE_ENTERPRISE=

# Seguridad
CSRF_SECRET=              # String aleatorio ≥32 chars
ADMIN_API_KEY=            # Clave para el dashboard de admin
ALLOWED_EMAIL_DOMAIN=loggro.com

# Servidor
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:5173

# Base de datos
DATABASE_PATH=./data/portal.db

# Archivos
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,image/webp,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

# Rate limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=5
```

### 9.3 Producción (contenedor)

```dockerfile
# Backend
FROM node:20-alpine
WORKDIR /app
COPY backend/package*.json ./
RUN npm ci --production
COPY backend/dist ./dist
COPY backend/.env.production .env
CMD ["node", "dist/server.js"]
```

```dockerfile
# Frontend (Nginx)
FROM nginx:alpine
COPY frontend/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 9.4 Railway / Render / VPS

El backend sirve el frontend compilado en producción (`express.static`). Un solo servicio, un solo puerto. Variables de entorno configuradas en el panel del proveedor.

---

## 10. Decisiones de Diseño

### ¿Por qué SQLite y no PostgreSQL?

Para el MVP con uso interno (decenas de tickets al día), SQLite es más que suficiente. No requiere servidor, backup es copiar un archivo, y better-sqlite3 es completamente síncrono — elimina complejidad de conexiones y pool. La migración a PostgreSQL en el futuro requiere cambiar solo `database/connection.ts` y adaptar el SQL.

### ¿Por qué token CSRF stateless (HMAC) y no csurf?

`csurf` fue deprecado. El token HMAC-SHA256 es stateless (compatible con múltiples réplicas), no requiere sesión de servidor, y es compatible con SSO futuro donde el JWT ya provee identidad.

### ¿Por qué config en SQLite y no en archivos JSON?

La config en base de datos permite modificarla desde el Admin Dashboard sin acceso al servidor ni reinicio del proceso. Un archivo JSON requeriría acceso SSH o un sistema de archivos compartido en producción con múltiples réplicas.

### ¿Por qué no usar el SDK oficial de Intercom?

El SDK de Node.js de Intercom tiene buen soporte, pero para los 3 endpoints que usamos (`/contacts/search`, `/contacts`, `/tickets`), el overhead de una dependencia grande no aporta valor. Usamos `axios` con tipado TypeScript propio — más ligero y más controlable para manejo de errores específicos.

### ¿Por qué React Router en lugar de Next.js?

El portal es una SPA sencilla con 3 páginas. Next.js agrega complejidad de SSR innecesaria. Vite + React Router da un bundle más pequeño, desarrollo más rápido y despliegue más simple (archivos estáticos servidos por Express o Nginx).

---

## 11. Roadmap SSO y Extensiones Futuras

### Autenticación SSO (próxima versión)

```
Microsoft Entra ID:
  Backend agrega ruta GET /auth/microsoft → redirige a Azure AD
  Backend recibe callback POST /auth/microsoft/callback
  Valida el JWT del token de Entra ID
  Extrae email, name, groups del claim
  Genera JWT interno firmado con JWT_SECRET
  Frontend almacena JWT en memoria (no localStorage)
  domainAuth middleware reemplaza regex por verificación de JWT claim

Google Workspace:
  Mismo patrón con Google OAuth2
```

### Notificaciones por correo

```
Servicio: services/emailService.ts
Triggered desde: ticketController después de crear ticket exitosamente
Template: HTML con número de ticket, fecha, producto, prioridad
Provider: SendGrid / Resend (env var EMAIL_PROVIDER)
```

### Consulta de estado del ticket

```
Ruta: GET /api/tickets/:intercomTicketId/status
Implementación: intercomService.getTicket(id)
UI: Nueva página /ticket/:id con estado, comentarios, asignado
```

### Notificaciones en tiempo real

```
WebSocket o Server-Sent Events desde el backend
Intercom Webhook → backend recibe eventos de cambio de estado
Actualiza SQLite → emite SSE al browser si tiene la página abierta
```
