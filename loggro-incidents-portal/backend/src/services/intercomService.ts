import axios, { AxiosInstance } from 'axios';
import { config } from '../config';
import { logger } from '../utils/logger';

interface IntercomContact {
  id: string;
  email: string;
  name?: string;
}

interface IntercomTicket {
  id: string;
  ticket_url?: string;
  ticket_attributes?: Record<string, unknown>;
}

interface CreateTicketParams {
  contactId: string;
  ticketTypeId: string;
  title: string;
  description: string;
  product: string;
  requestType: string;
  priority: string;
  companyName?: string;
  companyNit?: string;
  operationalImpact?: string;
  requesterTeam?: string;
  dynamicAttributes?: Record<string, string>;
}

export class IntercomService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: 'https://api.intercom.io',
      headers: {
        Authorization: `Bearer ${config.intercom.accessToken}`,
        'Intercom-Version': config.intercom.apiVersion,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      timeout: 15000,
    });

    this.client.interceptors.request.use((req) => {
      logger.debug('Intercom API request', { method: req.method?.toUpperCase(), url: req.url });
      return req;
    });

    this.client.interceptors.response.use(
      (res) => {
        logger.debug('Intercom API response', { status: res.status, url: res.config.url });
        return res;
      },
      (err) => {
        const status = err.response?.status;
        const body = err.response?.data;
        logger.error('Intercom API error', { status, body, url: err.config?.url });
        throw err;
      }
    );
  }

  async findOrCreateContact(email: string, name: string): Promise<IntercomContact> {
    // Search for existing contact
    try {
      const searchRes = await this.client.post('/contacts/search', {
        query: {
          operator: 'AND',
          value: [{ field: 'email', operator: '=', value: email }],
        },
      });

      const contacts = searchRes.data?.data;
      if (contacts && contacts.length > 0) {
        logger.info('Intercom contact found', { email, contactId: contacts[0].id });
        return { id: contacts[0].id, email: contacts[0].email, name: contacts[0].name };
      }
    } catch (err) {
      logger.warn('Intercom contact search failed, will attempt creation', { email });
    }

    // Create new contact
    const createRes = await this.client.post('/contacts', {
      role: 'user',
      email,
      name,
    });

    logger.info('Intercom contact created', { email, contactId: createRes.data.id });
    return { id: createRes.data.id, email: createRes.data.email, name: createRes.data.name };
  }

  async createTicket(params: CreateTicketParams): Promise<IntercomTicket> {
    const title = `[${params.product.toUpperCase()}] ${params.requestType} — ${params.companyName || 'Sin empresa'}`;
    const descriptionFull = this.buildDescription(params);

    const ticketAttributes: Record<string, unknown> = {
      _default_title_: title,
      _default_description_: descriptionFull,
    };

    // Merge any dynamic attributes from the form
    if (params.dynamicAttributes) {
      Object.assign(ticketAttributes, params.dynamicAttributes);
    }

    const payload: Record<string, unknown> = {
      contacts: [{ id: params.contactId }],
      ticket_attributes: ticketAttributes,
    };

    // Only include ticket_type_id if configured
    if (params.ticketTypeId) {
      payload.ticket_type_id = params.ticketTypeId;
    }

    const res = await this.client.post('/tickets', payload);

    logger.info('Intercom ticket created', {
      ticketId: res.data.id,
      product: params.product,
      priority: params.priority,
    });

    return {
      id: String(res.data.id),
      ticket_url: res.data.ticket_url,
      ticket_attributes: res.data.ticket_attributes,
    };
  }

  private buildDescription(params: CreateTicketParams): string {
    const lines = [
      `**Producto:** ${params.product}`,
      `**Tipo de solicitud:** ${params.requestType}`,
      `**Prioridad:** ${params.priority}`,
      params.companyName ? `**Empresa:** ${params.companyName}` : null,
      params.companyNit  ? `**NIT:** ${params.companyNit}` : null,
      params.operationalImpact ? `**Impacto operativo:** ${params.operationalImpact}` : null,
      '',
      `**Descripción:**`,
      params.description,
    ].filter((l) => l !== null);

    if (params.dynamicAttributes && Object.keys(params.dynamicAttributes).length) {
      lines.push('', '**Información adicional:**');
      for (const [key, value] of Object.entries(params.dynamicAttributes)) {
        lines.push(`- ${key}: ${value}`);
      }
    }

    return lines.join('\n');
  }
}

export const intercomService = new IntercomService();
