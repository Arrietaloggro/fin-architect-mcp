import 'dotenv/config';
import app from './app';
import { config } from './config';
import { logger } from './utils/logger';
import { runMigrations } from './database/migrations';
import { closeDb } from './database/connection';

function validateStartup(): void {
  const warnings: string[] = [];

  if (!config.intercom.accessToken) {
    warnings.push('INTERCOM_ACCESS_TOKEN no configurado — la creación de tickets fallará');
  }
  if (config.security.csrfSecret.includes('dev-')) {
    warnings.push('CSRF_SECRET es el valor por defecto — cambia esto en producción');
  }
  if (config.security.adminApiKey.includes('dev-')) {
    warnings.push('ADMIN_API_KEY es el valor por defecto — cambia esto en producción');
  }
  if (config.isProduction && config.cors.origin.includes('localhost')) {
    warnings.push('CORS_ORIGIN apunta a localhost en modo producción');
  }

  // Check Intercom ticket types in production
  if (config.intercom.accessToken && config.isProduction) {
    const missing = Object.entries(config.intercom.ticketTypes)
      .filter(([, v]) => !v)
      .map(([k]) => k);
    if (missing.length) {
      warnings.push(`Ticket Type IDs no configurados para: ${missing.join(', ')}`);
    }
  }

  if (warnings.length) {
    warnings.forEach((w) => logger.warn(`Startup warning: ${w}`));
  }
}

async function main() {
  try {
    runMigrations();
    validateStartup();

    const server = app.listen(config.port, () => {
      logger.info('Server started', { port: config.port, env: config.env });
      logger.info(`Health:  http://localhost:${config.port}/health`);
      logger.info(`API:     http://localhost:${config.port}/api`);
    });

    // Graceful shutdown — handles Railway SIGTERM and Ctrl+C
    const shutdown = (signal: string) => {
      logger.info(`${signal} received — shutting down gracefully`);
      server.close(() => {
        closeDb();
        logger.info('Server closed');
        process.exit(0);
      });
      // Force exit after 10s if connections don't close
      setTimeout(() => process.exit(1), 10_000).unref();
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT',  () => shutdown('SIGINT'));
    process.on('uncaughtException', (err) => {
      logger.error('Uncaught exception', { error: err.message, stack: err.stack });
      shutdown('uncaughtException');
    });
    process.on('unhandledRejection', (reason) => {
      logger.error('Unhandled promise rejection', { reason });
    });

  } catch (err) {
    logger.error('Failed to start server', { error: err instanceof Error ? err.message : err });
    process.exit(1);
  }
}

main();
