import React, { useState, useEffect } from 'react';
import { adminApi } from '../services/api';
import { PortalConfig } from '../types';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { PageWrapper } from '../components/layout/PageWrapper';

// Re-using the PortalConfig type from admin perspective
type AdminConfig = {
  products: Array<{ id: string; name: string; icon: string; active: boolean; description: string; intercomTicketTypeId: string }>;
  requestTypes: Array<{ id: string; name: string; active: boolean }>;
  priorities: Array<{ id: string; name: string; color: string; slaHours: number; description: string }>;
  teams: Array<{ id: string; name: string }>;
};

type Stats = {
  total: number;
  today: number;
  byStatus: Array<{ status: string; count: number }>;
  byProduct: Array<{ product: string; count: number }>;
  byPriority: Array<{ priority: string; count: number }>;
};

type HistoryRecord = {
  id: number;
  created_at: string;
  requester_name: string;
  requester_email: string;
  company_name?: string;
  product: string;
  request_type: string;
  priority: string;
  intercom_ticket_id?: string;
  status: string;
  response_time_ms?: number;
};

const PRIORITY_COLORS: Record<string, 'red' | 'orange' | 'yellow' | 'green'> = {
  critical: 'red', high: 'orange', medium: 'yellow', low: 'green',
};

const STATUS_COLORS: Record<string, 'green' | 'red' | 'yellow'> = {
  success: 'green', error: 'red', pending: 'yellow',
};

export function Admin() {
  const [apiKey, setApiKey] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');
  const [activeTab, setActiveTab] = useState<'stats' | 'config' | 'history'>('stats');

  const [config, setConfig] = useState<AdminConfig | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<{ records: HistoryRecord[]; total: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticate = async () => {
    setAuthError('');
    try {
      const data = await adminApi.getStats(apiKey);
      setStats(data);
      setAuthenticated(true);
    } catch {
      setAuthError('API Key inválida. Verifica la configuración.');
    }
  };

  useEffect(() => {
    if (!authenticated) return;
    setLoading(true);
    Promise.all([
      adminApi.getConfig(apiKey),
      adminApi.getStats(apiKey),
      adminApi.getHistory({}, apiKey),
    ]).then(([cfg, sts, hist]) => {
      setConfig(cfg);
      setStats(sts);
      setHistory(hist);
    }).catch(() => setError('Error cargando datos del admin.'))
      .finally(() => setLoading(false));
  }, [authenticated]);

  const saveConfig = async () => {
    if (!config) return;
    setSaving(true);
    try {
      await adminApi.updateConfig(config, apiKey);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError('Error guardando configuración.');
    } finally {
      setSaving(false);
    }
  };

  const toggleProduct = (id: string) => {
    if (!config) return;
    setConfig({
      ...config,
      products: config.products.map((p) => p.id === id ? { ...p, active: !p.active } : p),
    });
  };

  const toggleRequestType = (id: string) => {
    if (!config) return;
    setConfig({
      ...config,
      requestTypes: config.requestTypes.map((r) => r.id === id ? { ...r, active: !r.active } : r),
    });
  };

  const updateTicketTypeId = (productId: string, value: string) => {
    if (!config) return;
    setConfig({
      ...config,
      products: config.products.map((p) => p.id === productId ? { ...p, intercomTicketTypeId: value } : p),
    });
  };

  if (!authenticated) {
    return (
      <PageWrapper>
        <div className="max-w-sm mx-auto py-16 animate-fade-in">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-loggro-100 rounded-xl flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-loggro-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">Acceso Administrativo</h1>
            <p className="text-sm text-gray-500 mt-1">Ingresa la API Key de administrador</p>
          </div>
          <Card>
            <div className="flex flex-col gap-4">
              <Input
                label="API Key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && authenticate()}
                placeholder="tu-api-key-aquí"
                error={authError}
              />
              <Button onClick={authenticate} disabled={!apiKey.trim()} className="w-full">
                Acceder al panel
              </Button>
            </div>
          </Card>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Panel de Administración</h1>
          <p className="text-sm text-gray-500">Portal Interno de Incidencias Loggro</p>
        </div>
        {activeTab === 'config' && (
          <Button onClick={saveConfig} loading={saving} size="sm">
            {saved ? '✓ Guardado' : 'Guardar cambios'}
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit">
        {(['stats', 'config', 'history'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
              activeTab === tab ? 'bg-white shadow text-gray-900' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {{ stats: 'Estadísticas', config: 'Configuración', history: 'Historial' }[tab]}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spinner text="Cargando..." /></div>
      ) : error ? (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">{error}</div>
      ) : (
        <>
          {/* Stats tab */}
          {activeTab === 'stats' && stats && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 animate-fade-in">
              <Card className="text-center">
                <p className="text-3xl font-bold text-loggro-600">{stats.total}</p>
                <p className="text-xs text-gray-500 mt-1">Total tickets</p>
              </Card>
              <Card className="text-center">
                <p className="text-3xl font-bold text-emerald-600">{stats.today}</p>
                <p className="text-xs text-gray-500 mt-1">Hoy</p>
              </Card>
              <Card className="col-span-2">
                <p className="text-xs font-medium text-gray-700 mb-2">Por producto</p>
                {stats.byProduct.slice(0, 5).map((r) => (
                  <div key={r.product} className="flex justify-between text-sm py-0.5">
                    <span className="text-gray-600 uppercase text-xs">{r.product}</span>
                    <span className="font-semibold">{r.count}</span>
                  </div>
                ))}
              </Card>
              <Card className="col-span-2">
                <p className="text-xs font-medium text-gray-700 mb-2">Por estado</p>
                {stats.byStatus.map((r) => (
                  <div key={r.status} className="flex justify-between items-center text-sm py-0.5">
                    <Badge color={STATUS_COLORS[r.status] || 'gray'} size="sm">{r.status}</Badge>
                    <span className="font-semibold">{r.count}</span>
                  </div>
                ))}
              </Card>
              <Card className="col-span-2">
                <p className="text-xs font-medium text-gray-700 mb-2">Por prioridad</p>
                {stats.byPriority.map((r) => (
                  <div key={r.priority} className="flex justify-between items-center text-sm py-0.5">
                    <Badge color={PRIORITY_COLORS[r.priority] || 'gray'} size="sm">{r.priority}</Badge>
                    <span className="font-semibold">{r.count}</span>
                  </div>
                ))}
              </Card>
            </div>
          )}

          {/* Config tab */}
          {activeTab === 'config' && config && (
            <div className="flex flex-col gap-6 animate-fade-in">
              <Card>
                <CardHeader>
                  <h2 className="font-semibold text-gray-900">Productos activos</h2>
                  <p className="text-xs text-gray-500 mt-0.5">Activa o desactiva productos y configura los Ticket Type ID de Intercom</p>
                </CardHeader>
                <div className="flex flex-col gap-4">
                  {config.products.map((p) => (
                    <div key={p.id} className={`rounded-lg border p-4 transition-colors ${p.active ? 'border-loggro-200 bg-loggro-50' : 'border-gray-200'}`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{p.icon}</span>
                          <span className="font-medium text-sm text-gray-900">{p.name}</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => toggleProduct(p.id)}
                          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${p.active ? 'bg-loggro-600' : 'bg-gray-300'}`}
                        >
                          <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${p.active ? 'translate-x-4' : 'translate-x-0.5'}`} />
                        </button>
                      </div>
                      <Input
                        label="Intercom Ticket Type ID"
                        value={p.intercomTicketTypeId}
                        onChange={(e) => updateTicketTypeId(p.id, e.target.value)}
                        placeholder="ID del Ticket Type en Intercom"
                        hint="Encontrar en: Intercom → Settings → Tickets → Ticket Types"
                      />
                    </div>
                  ))}
                </div>
              </Card>

              <Card>
                <CardHeader>
                  <h2 className="font-semibold text-gray-900">Tipos de solicitud</h2>
                </CardHeader>
                <div className="flex flex-col gap-2">
                  {config.requestTypes.map((r) => (
                    <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                      <span className="text-sm text-gray-700">{r.name}</span>
                      <button
                        type="button"
                        onClick={() => toggleRequestType(r.id)}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${r.active ? 'bg-loggro-600' : 'bg-gray-300'}`}
                      >
                        <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${r.active ? 'translate-x-4' : 'translate-x-0.5'}`} />
                      </button>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* History tab */}
          {activeTab === 'history' && history && (
            <div className="animate-fade-in">
              <Card padding="none" className="overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                  <h2 className="font-semibold text-gray-900">Historial de tickets</h2>
                  <span className="text-xs text-gray-500">{history.total} registros</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                      <tr>
                        {['Fecha', 'Solicitante', 'Empresa', 'Producto', 'Prioridad', 'Ticket ID', 'Estado', 'Tiempo'].map((h) => (
                          <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {history.records.map((r) => (
                        <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                            {new Date(r.created_at).toLocaleDateString('es-CO')}
                          </td>
                          <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{r.requester_name}</td>
                          <td className="px-4 py-3 text-gray-600">{r.company_name || '—'}</td>
                          <td className="px-4 py-3"><Badge color="blue" size="sm">{r.product}</Badge></td>
                          <td className="px-4 py-3"><Badge color={PRIORITY_COLORS[r.priority] || 'gray'} size="sm">{r.priority}</Badge></td>
                          <td className="px-4 py-3 font-mono text-xs text-gray-600">
                            {r.intercom_ticket_id ? `#${r.intercom_ticket_id}` : '—'}
                          </td>
                          <td className="px-4 py-3"><Badge color={STATUS_COLORS[r.status] || 'gray'} size="sm">{r.status}</Badge></td>
                          <td className="px-4 py-3 text-gray-500 text-xs">{r.response_time_ms ? `${r.response_time_ms}ms` : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {history.records.length === 0 && (
                    <p className="text-center text-gray-500 text-sm py-12">No hay registros todavía.</p>
                  )}
                </div>
              </Card>
            </div>
          )}
        </>
      )}
    </PageWrapper>
  );
}
