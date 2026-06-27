import { Request, Response, NextFunction } from 'express';
import { config } from '../config';
import { logger } from '../utils/logger';

const DOMAIN_REGEX = /^[a-zA-Z0-9._%+\-]+@loggro\.com$/i;

export function domainAuth(req: Request, res: Response, next: NextFunction): void {
  const email: string | undefined =
    req.body?.requesterEmail || req.body?.email || req.query?.email as string;

  if (!email) {
    res.status(400).json({ error: 'Email corporativo requerido' });
    return;
  }

  const domain = config.security.allowedEmailDomain;
  const allowed = new RegExp(`^[a-zA-Z0-9._%+\\-]+@${domain.replace('.', '\\.')}$`, 'i');

  if (!allowed.test(email)) {
    logger.warn('Blocked non-corporate email attempt', { email: email.substring(0, 20), ip: req.ip });
    res.status(403).json({
      error: `Acceso restringido. Solo se permiten correos @${domain}.`,
    });
    return;
  }

  next();
}
