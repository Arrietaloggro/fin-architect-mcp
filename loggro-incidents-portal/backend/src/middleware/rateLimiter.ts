import rateLimit from 'express-rate-limit';
import { config } from '../config';
import { logger } from '../utils/logger';

export const ticketRateLimiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: 'Demasiadas solicitudes. Por favor espera unos minutos antes de intentar nuevamente.',
    retryAfter: Math.ceil(config.rateLimit.windowMs / 1000 / 60),
  },
  handler: (req, res, next, options) => {
    logger.warn('Rate limit exceeded', { ip: req.ip, path: req.path });
    res.status(429).json(options.message);
  },
});

export const configRateLimiter = rateLimit({
  windowMs: 60_000,
  max: 60,
  standardHeaders: true,
  legacyHeaders: false,
});

export const adminRateLimiter = rateLimit({
  windowMs: 60_000,
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
});
