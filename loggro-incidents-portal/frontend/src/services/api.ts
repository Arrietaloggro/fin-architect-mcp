import axios, { AxiosError } from 'axios';
import { PortalConfig, TicketFormData, TicketResult } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Response interceptor: normalize error messages
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ error?: string }>) => {
    if (err.code === 'ECONNABORTED') {
      throw new Error('La solicitud tardó demasiado. Verifica tu conexión e intenta nuevamente.');
    }
    if (!err.response) {
      throw new Error('No se pudo conectar con el servidor. Verifica tu conexión a Internet.');
    }
    throw err;
  }
);

let csrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken;
  const res = await api.get<{ csrfToken: string }>('/config/csrf-token');
  csrfToken = res.data.csrfToken;
  return csrfToken;
}

// Invalidate CSRF token on any 403 so the next request gets a fresh one
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 403) csrfToken = null;
    throw err;
  }
);

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

  // Invalidate token after successful use (one-time use)
  csrfToken = null;
  return res.data;
}

// Admin API — separate axios instance (no CSRF needed, uses Bearer token)
const adminAxios = axios.create({ baseURL: '/api', timeout: 15000 });

export const adminApi = {
  getConfig: (key: string) =>
    adminAxios.get('/admin/config', { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  updateConfig: (cfg: unknown, key: string) =>
    adminAxios.put('/admin/config', cfg, { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  patchSection: (section: string, data: unknown, key: string) =>
    adminAxios.patch(`/admin/config/${section}`, data, { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  getHistory: (params: Record<string, unknown>, key: string) =>
    adminAxios.get('/admin/history', { params, headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),

  getStats: (key: string) =>
    adminAxios.get('/admin/stats', { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.data),
};
