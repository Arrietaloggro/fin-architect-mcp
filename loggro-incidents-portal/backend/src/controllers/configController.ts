import { Request, Response } from 'express';
import { PortalConfigModel } from '../models/PortalConfig';

export function getPublicConfig(req: Request, res: Response): void {
  try {
    const cfg = PortalConfigModel.get();
    // Return only active items to the public form
    res.json({
      products: cfg.products.filter((p) => p.active),
      requestTypes: cfg.requestTypes.filter((r) => r.active),
      priorities: cfg.priorities,
      teams: cfg.teams,
    });
  } catch (err) {
    res.status(500).json({ error: 'Error cargando la configuración del portal.' });
  }
}
