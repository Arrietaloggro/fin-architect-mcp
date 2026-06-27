import axios from 'axios';
import { PortalConfig, TicketFormData, TicketResult } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

let csrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken;
  const res = await api.get<{ csrfToken: string }>('/config/csrf-token');
  csrfToken = res.data.csrfToken;
  return csrfToken;
}

export async function fetchPortalConfig(): Promise<PortalConfig> {
  const res = await api.get<PortalConfig>('/config');
  return res.data;
}

export async function submitTicket(formData: TicketFormData): Promise<TicketResult> {
  const token = await getCsrfToken();

  const body = new FormData();
  body.append('requesterName', formData.requesterName);
  body.append('requesterEmail', formData.requesterEmail);
  body.append('companyName', formData.companyName);
  body.append('companyNit', formData.companyNit);
  body.append('product', formData.product);
  body.append('requestType', formData.requestType);
  body.append('priority', formData.priority);
  body.append('operationalImpact', formData.operationalImpact);
  body.append('description', formData.description);
  body.append('dynamicFields', JSON.stringify(formData.dynamicFields));

  for (const file of formData.attachments) {
    body.append('attachments', file);
  }

  const res = await api.post<TicketResult>('/tickets', body, {
    headers: {
      'X-CSRF-Token': token,
      'Content-Type': 'multipart/form-data',
    },
  });

  // Invalidate token after use
  csrfToken = null;
  return res.data;
}

// Admin API
export const adminApi = {
  getConfig: (key: string) =>
    axios.get('/api/admin/config', { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  updateConfig: (config: unknown, key: string) =>
    axios.put('/api/admin/config', config, { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  patchSection: (section: string, data: unknown, key: string) =>
    axios.patch(`/api/admin/config/${section}`, data, { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  getHistory: (params: Record<string, unknown>, key: string) =>
    axios.get('/api/admin/history', { params, headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  getStats: (key: string) =>
    axios.get('/api/admin/stats', { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),
};
