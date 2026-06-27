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
    const data = req.body as PortalConfigData;
    // Basic shape validation
    if (!data.products || !data.requestTypes || !data.priorities || !data.teams) {
      res.status(400).json({ error: 'Configuración inválida: faltan secciones requeridas (products, requestTypes, priorities, teams).' });
      return;
    }
    PortalConfigModel.set(data);
    logger.info('Portal config updated via admin dashboard', { requestId: req.requestId });
    res.json({ success: true, config: PortalConfigModel.get() });
  } catch (err) {
    res.status(400).json({ error: 'Configuración inválida.' });
  }
}

export function patchSection(section: keyof PortalConfigData) {
  return (req: Request, res: Response): void => {
    try {
      if (!Array.isArray(req.body)) {
        res.status(400).json({ error: `El cuerpo de la solicitud debe ser un array para la sección ${section}.` });
        return;
      }
      const update: Partial<PortalConfigData> = { [section]: req.body } as Partial<PortalConfigData>;
      const updated = PortalConfigModel.patch(update);
      logger.info(`Admin patched config section: ${section}`, { requestId: req.requestId });
      res.json({ success: true, [section]: updated[section] });
    } catch (err) {
      res.status(400).json({ error: `Error actualizando ${section}.` });
    }
  };
}

export function getHistory(req: Request, res: Response): void {
  try {
    const { page, limit, product, status, startDate, endDate, email } = req.query;
    const pageNum = page ? parseInt(page as string, 10) : 1;
    const limitNum = Math.min(limit ? parseInt(limit as string, 10) : 20, 100); // max 100 per page
    if (isNaN(pageNum) || pageNum < 1 || isNaN(limitNum) || limitNum < 1) {
      res.status(400).json({ error: 'Parámetros de paginación inválidos.' });
      return;
    }
    const result = TicketHistoryModel.findAll({
      page: pageNum,
      limit: limitNum,
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
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) { res.status(400).json({ error: 'ID inválido.' }); return; }
  const record = TicketHistoryModel.findById(id);
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
