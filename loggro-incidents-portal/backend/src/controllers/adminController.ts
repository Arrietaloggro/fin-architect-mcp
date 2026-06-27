import { Request, Response } from 'express';
import { PortalConfigModel, PortalConfigData } from '../models/PortalConfig';
import { TicketHistoryModel } from '../models/TicketHistory';
import { logger } from '../utils/logger';

export function getConfig(req: Request, res: Response): void {
  try {
    res.json(PortalConfigModel.get());
  } catch (err) {
    res.status(500).json({ error: 'Error leyendo configuración.' });
  }
}

export function updateConfig(req: Request, res: Response): void {
  try {
    PortalConfigModel.set(req.body as PortalConfigData);
    logger.info('Portal config updated via admin dashboard');
    res.json({ success: true, config: PortalConfigModel.get() });
  } catch (err) {
    res.status(400).json({ error: 'Configuración inválida.' });
  }
}

export function patchSection(section: keyof PortalConfigData) {
  return (req: Request, res: Response): void => {
    try {
      const updated = PortalConfigModel.patch({ [section]: req.body } as Partial<PortalConfigData>);
      logger.info(`Admin patched config section: ${section}`);
      res.json({ success: true, [section]: updated[section] });
    } catch (err) {
      res.status(400).json({ error: `Error actualizando ${section}.` });
    }
  };
}

export function getHistory(req: Request, res: Response): void {
  try {
    const { page, limit, product, status, startDate, endDate, email } = req.query;
    const result = TicketHistoryModel.findAll({
      page: page ? parseInt(page as string) : 1,
      limit: limit ? parseInt(limit as string) : 20,
      product: product as string | undefined,
      status: status as string | undefined,
      startDate: startDate as string | undefined,
      endDate: endDate as string | undefined,
      email: email as string | undefined,
    });
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'Error consultando historial.' });
  }
}

export function getHistoryById(req: Request, res: Response): void {
  const record = TicketHistoryModel.findById(parseInt(req.params.id));
  if (!record) { res.status(404).json({ error: 'Registro no encontrado.' }); return; }
  res.json(record);
}

export function getStats(req: Request, res: Response): void {
  try {
    res.json(TicketHistoryModel.getStats());
  } catch (err) {
    res.status(500).json({ error: 'Error calculando estadísticas.' });
  }
}
