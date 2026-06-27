import { Request, Response } from 'express';
import { PortalConfigModel, PortalConfigData } from '../models/PortalConfig';
import { TicketHistoryModel } from '../models/TicketHistory';
import { runIntercomSync, getLatestSyncStatus, getSyncHistory } from '../services/intercomDiscovery';
import { config } from '../config';
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

// ─── Intercom sync endpoints ──────────────────────────────────────────────────

export function getIntercomSyncStatus(req: Request, res: Response): void {
  try {
    const status = getLatestSyncStatus();
    res.json(status ?? { lastSync: null, workspace: null, ticketTypes: [], teams: [] });
  } catch (err) {
    res.status(500).json({ error: 'Error consultando estado de sincronización.' });
  }
}

export function getIntercomSyncHistory(req: Request, res: Response): void {
  try {
    const limit = Math.min(parseInt((req.query.limit as string) ?? '20', 10), 100);
    const logs = getSyncHistory(limit);
    res.json({
      logs: logs.map((l) => ({
        id: l.id,
        startedAt: l.started_at,
        finishedAt: l.finished_at,
        status: l.status,
        triggeredBy: l.triggered_by,
        changesCount: l.changes_json ? (JSON.parse(l.changes_json) as unknown[]).length : 0,
        changes: l.changes_json ? JSON.parse(l.changes_json) : [],
        error: l.error_message,
        durationMs: l.duration_ms,
      })),
    });
  } catch (err) {
    res.status(500).json({ error: 'Error consultando historial de sincronización.' });
  }
}

export async function triggerIntercomSync(req: Request, res: Response): Promise<void> {
  const token = config.intercom.accessToken;
  if (!token) {
    res.status(503).json({
      error: 'INTERCOM_ACCESS_TOKEN no configurado. Ejecuta: npm run intercom:sync',
    });
    return;
  }

  try {
    logger.info('Intercom sync triggered via API', { requestId: req.requestId });
    const result = await runIntercomSync(token, 'api');
    res.json({
      status: result.status,
      logId: result.logId,
      durationMs: result.durationMs,
      changesCount: result.changes.length,
      changes: result.changes,
      workspace: result.workspace,
      ticketTypesCount: result.ticketTypes.length,
      teamsCount: result.teams.length,
      adminsCount: result.admins.length,
      error: result.error,
    });
  } catch (err) {
    res.status(500).json({ error: 'Error durante la sincronización.' });
  }
}
