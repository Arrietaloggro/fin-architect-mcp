import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import { config } from '../config';

const TOKEN_TTL_MS = 60 * 60 * 1000; // 1 hour

function generateToken(fingerprint: string): string {
  const ts = Date.now();
  const hmac = crypto.createHmac('sha256', config.security.csrfSecret);
  hmac.update(`${fingerprint}:${ts}`);
  return `${ts}.${hmac.digest('hex')}`;
}

function verifyToken(token: string, fingerprint: string): boolean {
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [tsStr, sig] = parts;
  const ts = parseInt(tsStr, 10);
  if (isNaN(ts) || Date.now() - ts > TOKEN_TTL_MS) return false;
  const hmac = crypto.createHmac('sha256', config.security.csrfSecret);
  hmac.update(`${fingerprint}:${ts}`);
  const expected = hmac.digest('hex');
  return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
}

function getFingerprint(req: Request): string {
  return req.ip || 'unknown';
}

export function csrfTokenHandler(req: Request, res: Response): void {
  const token = generateToken(getFingerprint(req));
  res.json({ csrfToken: token });
}

export function csrfProtection(req: Request, res: Response, next: NextFunction): void {
  // Skip CSRF for safe methods
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) { next(); return; }

  const token = req.headers['x-csrf-token'] as string | undefined;
  if (!token || !verifyToken(token, getFingerprint(req))) {
    res.status(403).json({ error: 'Token CSRF inválido o expirado. Recarga la página.' });
    return;
  }
  next();
}
