import { Request, Response } from 'express';
import { intercomService } from '../services/intercomService';
import { TicketHistoryModel } from '../models/TicketHistory';
import { PortalConfigModel } from '../models/PortalConfig';
import { config } from '../config';
import { logger } from '../utils/logger';

const REQUIRED_FIELDS = ['requesterName', 'requesterEmail', 'companyName', 'product', 'requestType', 'priority', 'description'] as const;

function validateBody(body: Record<string, unknown>): string | null {
  for (const field of REQUIRED_FIELDS) {
    const val = body[field];
    if (!val || (typeof val === 'string' && !val.trim())) {
      return `Campo requerido faltante: ${field}`;
    }
  }
  const email = body.requesterEmail as string;
  if (!/^[a-zA-Z0-9._%+\-]+@loggro\.com$/i.test(email)) {
    return 'El correo debe ser un email corporativo @loggro.com';
  }
  const desc = body.description as string;
  if (desc.trim().length < 10) {
    return 'La descripción debe tener al menos 10 caracteres';
  }
  return null;
}

export async function createTicket(req: Request, res: Response): Promise<void> {
  const startTime = Date.now();

  // Validate required fields
  const validationError = validateBody(req.body);
  if (validationError) {
    res.status(400).json({ error: validationError });
    return;
  }

  const {
    requesterName,
    requesterEmail,
    companyName,
    companyNit,
    product,
    requestType,
    priority,
    operationalImpact,
    description,
  } = req.body as Record<string, string>;

  // Parse dynamic fields safely
  let dynamicFields: Record<string, string> = {};
  try {
    const raw = req.body.dynamicFields;
    if (raw) dynamicFields = typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    // non-critical, continue without dynamic fields
  }

  // Create history record immediately (pending status)
  const historyId = TicketHistoryModel.create({
    requester_name: requesterName,
    requester_email: requesterEmail,
    company_name: companyName,
    company_nit: companyNit,
    product,
    request_type: requestType,
    priority,
    operational_impact: operationalImpact,
    description,
    status: 'pending',
    ip_address: req.ip,
    user_agent: req.headers['user-agent']?.substring(0, 255),
  });

  try {
    // Get ticket type ID from dynamic config
    const portalConfig = PortalConfigModel.get();
    const productConfig = portalConfig.products.find((p) => p.id === product);
    const ticketTypeId = productConfig?.intercomTicketTypeId || config.intercom.ticketTypes[product] || '';

    if (!config.intercom.accessToken) {
      throw new Error('INTERCOM_ACCESS_TOKEN no configurado. Configura las variables de entorno.');
    }

    // Find or create Intercom contact
    const contact = await intercomService.findOrCreateContact(requesterEmail, requesterName);

    // Create ticket in Intercom
    const ticket = await intercomService.createTicket({
      contactId: contact.id,
      ticketTypeId,
      title: `[${product.toUpperCase()}] ${requestType}`,
      description,
      product,
      requestType,
      priority,
      companyName,
      companyNit,
      operationalImpact,
      dynamicAttributes: dynamicFields,
    });

    const responseTimeMs = Date.now() - startTime;

    TicketHistoryModel.updateStatus(historyId, 'success', ticket.id, ticket.ticket_url, undefined, responseTimeMs);

    logger.info('Ticket created successfully', {
      requestId: req.requestId,
      historyId,
      intercomTicketId: ticket.id,
      product,
      priority,
      responseTimeMs,
    });

    res.status(201).json({
      success: true,
      ticketId: ticket.id,
      ticketUrl: ticket.ticket_url,
      historyId,
      createdAt: new Date().toISOString(),
      product: productConfig?.name || product,
      priority,
      requesterName,
      companyName,
    });
  } catch (err: unknown) {
    const responseTimeMs = Date.now() - startTime;
    const errorMessage = err instanceof Error ? err.message : 'Error desconocido';

    TicketHistoryModel.updateStatus(historyId, 'error', undefined, undefined, errorMessage, responseTimeMs);

    logger.error('Failed to create ticket', {
      requestId: req.requestId,
      historyId,
      product,
      error: errorMessage,
      responseTimeMs,
    });

    // Don't expose internal error details in production
    const clientMessage = config.isProduction
      ? 'No se pudo crear el ticket. Por favor intenta nuevamente o contacta a soporte técnico.'
      : errorMessage;

    res.status(502).json({ error: clientMessage });
  }
}
