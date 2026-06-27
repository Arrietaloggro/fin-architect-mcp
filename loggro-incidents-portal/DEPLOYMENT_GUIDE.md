# Deployment Guide — Portal Interno de Incidencias Loggro

## Arquitectura de producción

```
[Usuario @loggro.com]
        │
        ▼
[Vercel — Frontend React]
  ↓ /api/* proxy
[Railway — Backend Node.js + Express]
  ↓
[SQLite — Volume Railway /data/portal.db]
  ↓
[Intercom API — Tickets]
```

---

## SQLite vs PostgreSQL para el MVP

**SQLite es suficiente para el MVP** con las siguientes condiciones:
- **Volumen Railway**: monta el archivo en `/data/portal.db` (persistente entre deploys)
- **Carga esperada**: < 50 tickets/día, 1 instancia del backend
- **Sin replicación**: SQLite no soporta múltiples escritores concurrentes

**Migrar a PostgreSQL cuando**:
- Se requiera alta disponibilidad (múltiples instancias del backend)
- > 500 tickets/día o carga concurrente alta
- Se necesite replicación o backups automáticos gestionados

Railway ofrece PostgreSQL gestionado — la migración requiere cambiar `better-sqlite3` por `pg` y adaptar queries.

---

## PASO 1 — Railway (Backend)

### 1.1 Crear el proyecto

1. Ir a [railway.app](https://railway.app) → **New Project**
2. Seleccionar **Deploy from GitHub repo**
3. Conectar el repositorio: `arrietaloggro/fin-architect-mcp`
4. En **Root Directory** configurar: `loggro-incidents-portal/backend`
5. Railway detectará `nixpacks.toml` automáticamente

### 1.2 Crear el Volumen para SQLite

> **Crítico**: sin volumen, los datos se pierden en cada deploy.

1. En el servicio Railway → pestaña **Settings** → sección **Volumes**
2. **Add Volume**
3. Mount Path: `/data`
4. Tamaño: 1 GB (suficiente para el MVP)

### 1.3 Variables de entorno en Railway

Ve a **Service → Variables** y agrega:

```env
NODE_ENV=production
DATABASE_PATH=/data/portal.db
INTERCOM_ACCESS_TOKEN=<tu_token_de_intercom>
INTERCOM_API_VERSION=2.11
CORS_ORIGIN=https://<tu-proyecto>.vercel.app
CSRF_SECRET=<64 chars hex — genera con: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))">
ADMIN_API_KEY=<48 chars hex — genera con: node -e "console.log(require('crypto').randomBytes(24).toString('hex'))">
ALLOWED_EMAIL_DOMAIN=loggro.com
LOG_LEVEL=info
MAX_FILE_SIZE_MB=10
MAX_FILES_PER_REQUEST=5
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=5
```

> `PORT` lo inyecta Railway automáticamente — no lo configures manualmente.

### 1.4 Verificar el deploy

```bash
# Health check
curl https://<tu-backend>.up.railway.app/health

# Respuesta esperada:
# {"status":"ok","timestamp":"...","env":"production","version":"1.0.0"}
```

### 1.5 Sincronización Intercom (automática al arrancar)

El backend ejecuta `intercom:sync` automáticamente al iniciar si `INTERCOM_ACCESS_TOKEN` está configurado. También puedes dispararlo manualmente:

```bash
# Desde el backend en Railway (vía API):
curl -X POST https://<tu-backend>.up.railway.app/api/admin/intercom/sync \
  -H "Authorization: Bearer <ADMIN_API_KEY>"

# O localmente (desde tu máquina):
cd loggro-incidents-portal/backend
INTERCOM_ACCESS_TOKEN=<token> npm run intercom:sync
```

---

## PASO 2 — Vercel (Frontend)

### 2.1 Crear el proyecto

1. Ir a [vercel.com](https://vercel.com) → **New Project**
2. Importar desde GitHub: `arrietaloggro/fin-architect-mcp`
3. En **Root Directory** configurar: `loggro-incidents-portal/frontend`
4. Framework: **Vite** (detectado automáticamente)

### 2.2 Variables de entorno en Vercel

Ve a **Project → Settings → Environment Variables**:

```env
VITE_API_BASE_URL=https://<tu-backend>.up.railway.app
BACKEND_URL=https://<tu-backend>.up.railway.app
```

> `BACKEND_URL` es usada por `vercel.json` para el proxy de `/api/*`.
> `VITE_API_BASE_URL` queda disponible para el frontend en tiempo de build.

### 2.3 Verificar el deploy

1. Ir a `https://<tu-proyecto>.vercel.app`
2. El formulario debe cargar con los 6 productos
3. Navegar a `https://<tu-proyecto>.vercel.app/admin` para el dashboard

---

## PASO 3 — Actualizar CORS en Railway

Una vez tengas la URL de Vercel, actualiza en Railway:

```
CORS_ORIGIN=https://<tu-proyecto>.vercel.app
```

Si quieres permitir también una URL personalizada:
```
CORS_ORIGIN=https://incidencias.loggro.com,https://<tu-proyecto>.vercel.app
```

---

## PASO 4 — Dominio personalizado (opcional)

### `incidencias.loggro.com` → Vercel

1. Vercel → Project → Settings → Domains → Add `incidencias.loggro.com`
2. En tu DNS (CloudFlare/Route53/etc):
   ```
   CNAME  incidencias  cname.vercel-dns.com
   ```
3. Vercel provisiona SSL automáticamente (Let's Encrypt)

---

## PASO 5 — Validación post-deploy

```bash
# 1. Health backend
curl https://<backend>.up.railway.app/health

# 2. Config API
curl https://<backend>.up.railway.app/api/config

# 3. Ticket Types (requiere token)
curl https://<backend>.up.railway.app/api/admin/intercom/status \
  -H "Authorization: Bearer <ADMIN_API_KEY>"

# 4. Crear ticket de prueba (desde tu máquina)
cd loggro-incidents-portal/backend
INTERCOM_ACCESS_TOKEN=<token> npm run intercom:test
```

---

## Checklist de producción

- [ ] Railway: servicio creado y desplegado
- [ ] Railway: Volume `/data` montado
- [ ] Railway: todas las variables de entorno configuradas
- [ ] Railway: health check responde `{"status":"ok"}`
- [ ] Vercel: proyecto creado y desplegado
- [ ] Vercel: `BACKEND_URL` y `VITE_API_BASE_URL` configurados
- [ ] Vercel: frontend carga sin errores en consola
- [ ] CORS: `CORS_ORIGIN` apunta al dominio de Vercel
- [ ] Intercom: `npm run intercom:sync` ejecutado exitosamente
- [ ] Intercom: todos los Ticket Types mapeados a productos
- [ ] Test: ticket real creado desde el formulario
- [ ] Test: confirmación muestra número de ticket
- [ ] Admin: dashboard accesible con `ADMIN_API_KEY`
- [ ] Admin: tab "Intercom Sync" muestra última sincronización

---

## Comandos de mantenimiento

```bash
# Re-sincronizar Intercom (si se crean nuevos Ticket Types)
npm run intercom:sync

# Verificar integración completa
npm run intercom:test

# Ejecutar suite de tests unitarios
npm run validate

# Build de producción
npm run build
```

---

## Seguridad — checklist

- [ ] `CSRF_SECRET` es aleatorio (mínimo 32 bytes)
- [ ] `ADMIN_API_KEY` es aleatorio y no compartido
- [ ] `.env` está en `.gitignore` (verificado)
- [ ] `INTERCOM_ACCESS_TOKEN` solo en variables del servidor (nunca en frontend)
- [ ] `ALLOWED_EMAIL_DOMAIN=loggro.com` configurado
- [ ] Rate limiting activo (`RATE_LIMIT_MAX_REQUESTS=5`)
- [ ] Helmet CSP activo en producción
- [ ] CORS restringido al dominio del frontend

---

## Riesgos conocidos

| Riesgo | Mitigación |
|--------|-----------|
| SQLite sin volumen → pérdida de datos en redeploy | Crear Volume Railway obligatorio |
| Token Intercom con IP allowlist → bloqueo desde Railway | Desactivar IP restriction o añadir IPs de Railway |
| CORS mal configurado → frontend no puede llamar al backend | `CORS_ORIGIN` debe coincidir exactamente con el dominio de Vercel |
| `ADMIN_API_KEY` expuesta → acceso al dashboard de admin | Mantenerla secreta, rotarla periódicamente |
| Rate limit agresivo en demos → usuarios bloqueados | Ajustar `RATE_LIMIT_MAX_REQUESTS` si es necesario |
