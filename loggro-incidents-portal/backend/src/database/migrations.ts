import { getDb } from './connection';
import { logger } from '../utils/logger';
import { config } from '../config';

const SCHEMA = `
-- ── Intercom live configuration (auto-synced) ─────────────────────────────────

CREATE TABLE IF NOT EXISTS intercom_workspace (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  workspace_id TEXT NOT NULL,
  name         TEXT NOT NULL,
  region       TEXT,
  timezone     TEXT,
  raw_json     TEXT,
  synced_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intercom_ticket_types (
  id              TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  description     TEXT,
  icon            TEXT,
  archived        INTEGER DEFAULT 0,
  product_key     TEXT,
  attributes_json TEXT,
  raw_json        TEXT,
  first_seen_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at      DATETIME
);

CREATE TABLE IF NOT EXISTS intercom_teams (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  raw_json      TEXT,
  first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at    DATETIME
);

CREATE TABLE IF NOT EXISTS intercom_admins (
  id             TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  email          TEXT NOT NULL,
  is_token_owner INTEGER DEFAULT 0,
  raw_json       TEXT,
  first_seen_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at     DATETIME
);

CREATE TABLE IF NOT EXISTS intercom_custom_attributes (
  id            TEXT PRIMARY KEY,
  model         TEXT NOT NULL,
  name          TEXT NOT NULL,
  full_name     TEXT,
  label         TEXT,
  data_type     TEXT,
  description   TEXT,
  options_json  TEXT,
  raw_json      TEXT,
  first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at    DATETIME
);

CREATE TABLE IF NOT EXISTS intercom_sync_log (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  finished_at  DATETIME,
  status       TEXT NOT NULL DEFAULT 'running',
  triggered_by TEXT DEFAULT 'manual',
  changes_json TEXT,
  error_message TEXT,
  duration_ms  INTEGER
);

-- ── Tickets & portal config ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ticket_history (
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

CREATE TABLE IF NOT EXISTS portal_config (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  config_key   TEXT UNIQUE NOT NULL,
  config_value TEXT NOT NULL,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
`;

const DEFAULT_CONFIG = {
  products: [
    {
      id: 'erp-pymes',
      name: 'ERP-PYMES',
      icon: '🏢',
      color: '#2563EB',
      active: true,
      description: 'Sistema ERP para pequeñas y medianas empresas',
      intercomTicketTypeId: config.intercom.ticketTypes['erp-pymes'],
      dynamicFields: [
        {
          id: 'erp_module',
          type: 'select',
          label: 'Módulo afectado',
          required: true,
          options: ['Facturación', 'Inventario', 'Contabilidad', 'Compras', 'RRHH', 'Nómina', 'Tesorería', 'Otro'],
        },
        {
          id: 'erp_version',
          type: 'text',
          label: 'Versión del sistema',
          required: false,
          placeholder: 'Ej: 4.2.1',
        },
      ],
    },
    {
      id: 'restobar',
      name: 'RESTOBAR',
      icon: '🍽️',
      color: '#D97706',
      active: true,
      description: 'Sistema para restaurantes y bares',
      intercomTicketTypeId: config.intercom.ticketTypes['restobar'],
      dynamicFields: [
        {
          id: 'restobar_area',
          type: 'select',
          label: 'Área afectada',
          required: true,
          options: ['Caja / POS', 'Cocina / KDS', 'Reservas', 'Delivery', 'Reportes', 'Otro'],
        },
      ],
    },
    {
      id: 'pos-tienda',
      name: 'POS TIENDA',
      icon: '🏪',
      color: '#7C3AED',
      active: true,
      description: 'Punto de venta para tiendas y retail',
      intercomTicketTypeId: config.intercom.ticketTypes['pos-tienda'],
      dynamicFields: [
        {
          id: 'pos_area',
          type: 'select',
          label: 'Área afectada',
          required: true,
          options: ['Ventas / Caja', 'Inventario', 'Clientes', 'Reportes', 'Impresión', 'Otro'],
        },
        {
          id: 'pos_serial',
          type: 'text',
          label: 'Serial del equipo',
          required: false,
          placeholder: 'Número de serie del POS',
        },
      ],
    },
    {
      id: 'nomina',
      name: 'NÓMINA',
      icon: '💼',
      color: '#059669',
      active: true,
      description: 'Sistema de gestión de nómina',
      intercomTicketTypeId: config.intercom.ticketTypes['nomina'],
      dynamicFields: [
        {
          id: 'nomina_periodo',
          type: 'select',
          label: 'Período de nómina afectado',
          required: true,
          options: ['Nómina quincenal', 'Nómina mensual', 'Liquidación', 'Vacaciones', 'Incapacidad', 'Prima', 'Otro'],
        },
        {
          id: 'nomina_empleados',
          type: 'text',
          label: 'Número de empleados afectados',
          required: false,
          placeholder: 'Ej: 25',
        },
      ],
    },
    {
      id: 'alojamientos',
      name: 'ALOJAMIENTOS',
      icon: '🏨',
      color: '#0891B2',
      active: true,
      description: 'Sistema para hoteles y alojamientos',
      intercomTicketTypeId: config.intercom.ticketTypes['alojamientos'],
      dynamicFields: [
        {
          id: 'hotel_area',
          type: 'select',
          label: 'Área afectada',
          required: true,
          options: ['Recepción / Check-in', 'Reservas', 'Facturación', 'Housekeeping', 'Reportes', 'Otro'],
        },
        {
          id: 'hotel_habitaciones',
          type: 'text',
          label: 'Habitaciones afectadas',
          required: false,
          placeholder: 'Ej: 101, 102, 205',
        },
      ],
    },
    {
      id: 'enterprise',
      name: 'ENTERPRISE',
      icon: '🏛️',
      color: '#DC2626',
      active: true,
      description: 'Soluciones enterprise y grandes empresas',
      intercomTicketTypeId: config.intercom.ticketTypes['enterprise'],
      dynamicFields: [
        {
          id: 'enterprise_module',
          type: 'select',
          label: 'Módulo afectado',
          required: true,
          options: ['BI / Reportes', 'Integración ERP', 'API', 'Multi-sede', 'Seguridad', 'Otro'],
        },
        {
          id: 'enterprise_env',
          type: 'select',
          label: 'Ambiente afectado',
          required: false,
          options: ['Producción', 'Staging', 'Desarrollo', 'Pruebas'],
        },
      ],
    },
  ],
  requestTypes: [
    { id: 'bug', name: 'Error / Bug', active: true },
    { id: 'feature', name: 'Solicitud de mejora', active: true },
    { id: 'support', name: 'Soporte operativo', active: true },
    { id: 'training', name: 'Capacitación', active: true },
    { id: 'configuration', name: 'Configuración', active: true },
    { id: 'other', name: 'Otro', active: true },
  ],
  priorities: [
    { id: 'critical', name: 'Crítica', color: 'red',    slaHours: 4,  description: 'Sistema caído o impacto crítico en producción' },
    { id: 'high',     name: 'Alta',    color: 'orange', slaHours: 8,  description: 'Funcionalidad principal afectada' },
    { id: 'medium',   name: 'Media',   color: 'yellow', slaHours: 24, description: 'Funcionalidad secundaria o workaround disponible' },
    { id: 'low',      name: 'Baja',    color: 'green',  slaHours: 72, description: 'Consulta, mejora o sin impacto operativo' },
  ],
  teams: [
    { id: 'comercial',        name: 'Comercial' },
    { id: 'implementaciones', name: 'Implementaciones' },
    { id: 'customer-success', name: 'Customer Success' },
    { id: 'producto',         name: 'Producto' },
    { id: 'tecnologia',       name: 'Tecnología' },
  ],
};

export function runMigrations(): void {
  const db = getDb();

  db.exec(SCHEMA);
  logger.info('Database schema applied');

  const existing = db.prepare("SELECT config_value FROM portal_config WHERE config_key = 'main'").get();
  if (!existing) {
    db.prepare("INSERT INTO portal_config (config_key, config_value) VALUES ('main', ?)").run(
      JSON.stringify(DEFAULT_CONFIG)
    );
    logger.info('Default configuration seeded');
  }
}
