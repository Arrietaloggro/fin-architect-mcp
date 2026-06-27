import { Request, Response, NextFunction } from 'express';
import { config } from '../config';

export function adminAuth(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers['authorization'];
  const token = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token || token !== config.security.adminApiKey) {
    res.status(401).json({ error: 'Acceso no autorizado al panel de administración.' });
    return;
  }
  next();
}
