import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const requestId = uuidv4().slice(0, 8);
  const startTime = Date.now();

  (req as Request & { requestId: string }).requestId = requestId;

  res.on('finish', () => {
    const ms = Date.now() - startTime;
    const level = res.statusCode >= 500 ? 'error' : res.statusCode >= 400 ? 'warn' : 'info';
    logger.log(level, `${req.method} ${req.path}`, {
      requestId,
      status: res.statusCode,
      ms,
      ip: req.ip,
      ua: req.headers['user-agent']?.substring(0, 80),
    });
  });

  next();
}
