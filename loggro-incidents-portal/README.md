# Portal Interno de Incidencias — Loggro

Portal web para que los equipos internos de Loggro registren tickets de soporte directamente en Intercom, sin abrir conversaciones de chat.

## Inicio rápido

```bash
# 1. Instalar dependencias (una sola vez)
cd loggro-incidents-portal
npm run install:all

# 2. Configurar variables de entorno
cd backend
cp .env.example .env
# Editar .env con tus valores reales

# 3. Levantar todo (backend + frontend)
cd ..
npm run dev
```

El portal estará disponible en: **http://localhost:5173**
El backend en: **http://localhost:3001**
El admin dashboard en: **http://localhost:5173/admin**

---

## Configuración obligatoria

Antes de usar, edita `backend/.env`:

### Intercom
1. Ve a **Intercom → Settings → Integrations → Developer Hub → Tu app → Auth**
2. Copia el **Access Token** y pégalo en `INTERCOM_ACCESS_TOKEN`
3. Ve a **Intercom → Settings → Tickets → Ticket Types**
4. Crea un Ticket Type por cada producto (ERP-PYMES, RESTOBAR, etc.)
5. Copia los IDs y pégalos en `INTERCOM_TICKET_TYPE_*`

### Seguridad
```bash
# Genera CSRF_SECRET:
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Genera ADMIN_API_KEY:
node -e "console.log(require('crypto').randomBytes(24).toString('base64url'))"
```

---

## Estructura del proyecto

```
loggro-incidents-portal/
├── backend/          # Node.js + Express + TypeScript
│   ├── src/
│   └── .env.example
├── frontend/         # React + Vite + Tailwind CSS
│   └── src/
├── ARCHITECTURE.md   # Documento de arquitectura completo
└── package.json      # Scripts raíz
```

---

## Rutas disponibles

| Ruta | Descripción |
|---|---|
| `/` | Formulario de registro de incidencias |
| `/confirmation` | Página de confirmación post-envío |
| `/admin` | Dashboard de administración (requiere API Key) |

### API del backend

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/config` | Configuración pública del portal |
| GET | `/api/config/csrf-token` | Token CSRF para el formulario |
| POST | `/api/tickets` | Crear ticket (multipart/form-data) |
| GET | `/api/admin/config` | Config completa (requiere Bearer token) |
| PUT | `/api/admin/config` | Actualizar config completa |
| GET | `/api/admin/history` | Historial de tickets |
| GET | `/api/admin/stats` | Estadísticas |
| GET | `/health` | Health check del servidor |

---

## Arquitectura SSO (futura)

El middleware de autenticación está diseñado para recibir un JWT de Microsoft Entra ID o Google Workspace. Para activarlo en el futuro:

1. Agrega las variables `AZURE_AD_TENANT_ID`, `AZURE_AD_CLIENT_ID`, etc.
2. Implementa el provider en `backend/src/middleware/domainAuth.ts`
3. El resto del código no requiere cambios

Ver `ARCHITECTURE.md` para el detalle completo.

---

## Comandos disponibles

```bash
npm run dev           # Levanta backend y frontend simultáneamente
npm run dev:backend   # Solo el backend (puerto 3001)
npm run dev:frontend  # Solo el frontend (puerto 5173)
npm run build         # Compilar todo para producción
npm run start         # Iniciar backend compilado
```

---

## Producción

```bash
npm run build
# El frontend compilado queda en frontend/dist/
# Configurar el backend para servir archivos estáticos desde frontend/dist/
node backend/dist/server.js
```

Variables de entorno adicionales para producción:
```
NODE_ENV=production
CORS_ORIGIN=https://tu-dominio.com
LOG_LEVEL=warn
```
