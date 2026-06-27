import winston from 'winston';
import { config } from '../config';

const { combine, timestamp, json, colorize, printf, errors } = winston.format;

const devFormat = combine(
  colorize(),
  timestamp({ format: 'HH:mm:ss' }),
  errors({ stack: true }),
  printf(({ level, message, timestamp, requestId, ...meta }) => {
    const rid = requestId ? ` [${requestId}]` : '';
    const extra = Object.keys(meta).length ? ' ' + JSON.stringify(meta) : '';
    return `${timestamp} ${level}${rid}: ${message}${extra}`;
  })
);

const prodFormat = combine(
  timestamp(),
  errors({ stack: true }),
  json()
);

export const logger = winston.createLogger({
  level: config.logging.level,
  defaultMeta: { service: 'loggro-incidents-portal' },
  format: config.isProduction ? prodFormat : devFormat,
  transports: [new winston.transports.Console()],
});
