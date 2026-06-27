import 'dotenv/config';
import app from './app';
import { config } from './config';
import { logger } from './utils/logger';
import { runMigrations } from './database/migrations';
import { closeDb } from './database/connection';

async function main() {
  try {
    runMigrations();

    const server = app.listen(config.port, () => {
      logger.info(`Server started`, { port: config.port, env: config.env });
      logger.info(`API ready at http://localhost:${config.port}/api`);
    });

    const shutdown = () => {
      logger.info('Shutting down gracefully...');
      server.close(() => {
        closeDb();
        process.exit(0);
      });
    };

    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);
  } catch (err) {
    logger.error('Failed to start server', { error: err instanceof Error ? err.message : err });
    process.exit(1);
  }
}

main();
