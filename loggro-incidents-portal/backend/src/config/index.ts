import path from 'path';

function required(key: string): string {
  const val = process.env[key];
  if (!val) throw new Error(`Missing required environment variable: ${key}`);
  return val;
}

function optional(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

function optionalNumber(key: string, defaultValue: number): number {
  const val = process.env[key];
  return val ? parseInt(val, 10) : defaultValue;
}

export const config = {
  env: optional('NODE_ENV', 'development'),
  port: optionalNumber('PORT', 3001),
  isProduction: optional('NODE_ENV', 'development') === 'production',

  cors: {
    origin: optional('CORS_ORIGIN', 'http://localhost:5173'),
  },

  security: {
    csrfSecret: optional('CSRF_SECRET', 'dev-csrf-secret-change-in-production-32chars'),
    adminApiKey: optional('ADMIN_API_KEY', 'dev-admin-key-change-in-production'),
    allowedEmailDomain: optional('ALLOWED_EMAIL_DOMAIN', 'loggro.com'),
  },

  intercom: {
    accessToken: optional('INTERCOM_ACCESS_TOKEN', ''),
    apiVersion: optional('INTERCOM_API_VERSION', '2.11'),
    ticketTypes: {
      'erp-pymes':      optional('INTERCOM_TICKET_TYPE_ERP_PYMES', ''),
      'restobar':       optional('INTERCOM_TICKET_TYPE_RESTOBAR', ''),
      'pos-tienda':     optional('INTERCOM_TICKET_TYPE_POS_TIENDA', ''),
      'nomina':         optional('INTERCOM_TICKET_TYPE_NOMINA', ''),
      'alojamientos':   optional('INTERCOM_TICKET_TYPE_ALOJAMIENTOS', ''),
      'enterprise':     optional('INTERCOM_TICKET_TYPE_ENTERPRISE', ''),
    } as Record<string, string>,
  },

  database: {
    path: optional('DATABASE_PATH', './data/portal.db'),
  },

  uploads: {
    maxFileSizeMb: optionalNumber('MAX_FILE_SIZE_MB', 10),
    maxFilesPerRequest: optionalNumber('MAX_FILES_PER_REQUEST', 5),
    allowedMimeTypes: optional(
      'ALLOWED_FILE_TYPES',
      'image/jpeg,image/png,image/gif,image/webp,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ).split(','),
  },

  rateLimit: {
    windowMs: optionalNumber('RATE_LIMIT_WINDOW_MS', 900000),
    maxRequests: optionalNumber('RATE_LIMIT_MAX_REQUESTS', 5),
  },

  logging: {
    level: optional('LOG_LEVEL', 'info'),
  },
} as const;

export type Config = typeof config;
