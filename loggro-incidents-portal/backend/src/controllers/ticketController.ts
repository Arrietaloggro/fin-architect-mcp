import { Request, Response } from 'express';
import { intercomService } from '../services/intercomService';
import { TicketHistoryModel } from '../models/TicketHistory';
import { PortalConfigModel } from '../models/PortalConfig';
import { config } from '../config';
import { logger } from '../utils/logger';

export async function createTicket(req: Request, res: Response): Promise<void> {
  const startTime = Date.now();

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
    dynamicFields,
  } = req.body;

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
      dynamicAttributes: dynamicFields || {},
    });

    const responseTimeMs = Date.now() - startTime;

    TicketHistoryModel.updateStatus(historyId, 'success', ticket.id, ticket.ticket_url, undefined, responseTimeMs);

    logger.info('Ticket created successfully', {
      historyId,
      intercomTicketId: ticket.id,
      product,
      priority,
      email: requesterEmail,
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
      historyId,
      product,
      email: requesterEmail,
      error: errorMessage,
      responseTimeMs,
    });

    res.status(502).json({
      error: 'No se pudo crear el ticket en Intercom. Por favor intenta nuevamente o contacta a soporte técnico.',
    });
  }
}
