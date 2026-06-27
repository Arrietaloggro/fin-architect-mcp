import React, { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../services/api';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { PageWrapper } from '../components/layout/PageWrapper';

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
  id: number; created_at: string; requester_name: string; requester_email: string;
  company_name?: string; product: string; request_type: string; priority: string;
  intercom_ticket_id?: string; status: string; response_time_ms?: number;
};

type SyncChange = { kind: string; id: string; name: string; detail?: string };

type SyncStatus = {
  lastSync: {
    id: number; startedAt: string; finishedAt: string | null; status: string;
    triggeredBy: string; durationMs: number | null; changesCount: number;
    changes: SyncChange[]; error: string | null;
  } | null;
  workspace: { workspace_id: string; name: string; region: string; timezone: string; synced_at: string } | null;
  ticketTypes: Array<{ id: string; name: string; productKey: string | null; archived: boolean; active: boolean }>;
  teams: Array<{ id: string; name: string }>;
};

type SyncLogEntry = {
  id: number; startedAt: string; finishedAt: string | null; status: string;
  triggeredBy: string; changesCount: number; changes: SyncChange[];
  error: string | null; durationMs: number | null;
};

const PRIORITY_COLORS: Record<string, 'red' | 'orange' | 'yellow' | 'green'> = {
  critical: 'red', high: 'orange', medium: 'yellow', low: 'green',
};
const STATUS_COLORS: Record<string, 'green' | 'red' | 'yellow'> = {
  success: 'green', error: 'red', pending: 'yellow',
};
const CHANGE_ICONS: Record<string, string> = {
  ticket_type_added: '➕', ticket_type_deleted: '🗑', ticket_type_renamed: '✏️',
  ticket_type_product_mapped: '🔗', ticket_type_attributes_changed: '📎',
  team_added: '➕', team_deleted: '🗑', team_renamed: '✏️',
  admin_added: '➕', admin_deleted: '🗑',
  custom_attr_added: '➕', custom_attr_deleted: '🗑',
  workspace_updated: '🔄',
};

function formatDuration(ms: number | null): string {
  if (!ms) return '—';
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'medium' });
}

// ─── Intercom Sync Panel ─────────────────────────────────────────────────────

function IntercomSyncPanel({ apiKey }: { apiKey: string }) {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [history, setHistory] = useState<SyncLogEntry[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [expandedLog, setExpandedLog] = useState<number | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [s, h] = await Promise.all([
        adminApi.getIntercomStatus(apiKey),
        adminApi.getIntercomSyncHistory(apiKey, 10),
      ]);
      setStatus(s);
      setHistory(h.logs ?? []);
    } catch {
      setLoadError('Error cargando estado de sincronización.');
    }
  }, [apiKey]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const result = await adminApi.triggerIntercomSync(apiKey);
      setSyncResult(
        result.status === 'success'
          ? `✅ Sync completado — ${result.changesCount} cambio(s) en ${formatDuration(result.durationMs)}`
          : `❌ Error: ${result.error}`
      );
      await loadData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error desconocido';
      setSyncResult(`❌ ${msg}`);
    } finally {
      setSyncing(false);
    }
  };

  if (loadError) {
    return <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">{loadError}</div>;
  }
  if (!status) {
    return <div className="flex justify-center py-8"><Spinner text="Cargando..." /></div>;
  }

  const lastSync = status.lastSync;
  const activeTypes = status.ticketTypes.filter((t) => t.active);
  const mappedCount = activeTypes.filter((t) => t.productKey).length;

  return (
    <div className="flex flex-col gap-6 animate-fade-in">

      {/* Status header card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-2xl font-bold text-loggro-600">{activeTypes.length}</p>
          <p className="text-xs text-gray-500 mt-1">Ticket Types activos</p>
          <p className="text-xs text-gray-400">{mappedCount} mapeados a productos</p>
        </Card>
        <Card className="text-center">
          <p className="text-2xl font-bold text-loggro-600">{status.teams.length}</p>
          <p className="text-xs text-gray-500 mt-1">Teams / Inboxes</p>
        </Card>
        <Card className="text-center">
          {lastSync ? (
            <>
              <Badge
                color={lastSync.status === 'success' ? 'green' : lastSync.status === 'error' ? 'red' : 'yellow'}
                size="sm"
              >
                {lastSync.status}
              </Badge>
              <p className="text-xs text-gray-500 mt-1">{formatDate(lastSync.finishedAt ?? lastSync.startedAt)}</p>
              <p className="text-xs text-gray-400">{formatDuration(lastSync.durationMs)}</p>
            </>
          ) : (
            <>
              <p className="text-2xl text-gray-300">—</p>
              <p className="text-xs text-gray-500 mt-1">Sin sincronización</p>
            </>
          )}
        </Card>
      </div>

      {/* Workspace info */}
      {status.workspace && (
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-gray-900">Workspace Intercom</h2>
          </CardHeader>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div><p className="text-xs text-gray-500">Nombre</p><p className="font-medium">{status.workspace.name}</p></div>
            <div><p className="text-xs text-gray-500">ID</p><p className="font-mono text-xs">{status.workspace.workspace_id}</p></div>
            <div><p className="text-xs text-gray-500">Región</p><p className="font-medium">{status.workspace.region || '—'}</p></div>
            <div><p className="text-xs text-gray-500">Timezone</p><p className="font-medium">{status.workspace.timezone || '—'}</p></div>
          </div>
        </Card>
      )}

      {/* Sync action */}
      <Card>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="font-semibold text-gray-900">Sincronizar con Intercom</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Descubre Ticket Types, Inboxes, Admins y Custom Attributes. Detecta cambios automáticamente.
            </p>
          </div>
          <Button onClick={handleSync} loading={syncing} size="sm">
            {syncing ? 'Sincronizando…' : '🔄 Sincronizar ahora'}
          </Button>
        </div>
        {syncResult && (
          <div className={`mt-3 rounded-lg p-3 text-sm ${syncResult.startsWith('✅') ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
            {syncResult}
          </div>
        )}
      </Card>

      {/* Ticket Types table */}
      <Card padding="none">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Ticket Types</h2>
          <p className="text-xs text-gray-500 mt-0.5">Mapeados automáticamente a productos por keywords</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                {['ID', 'Nombre', 'Producto mapeado', 'Estado'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {status.ticketTypes.length === 0 ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500 text-sm">
                  Sin ticket types. Ejecuta una sincronización o crea Ticket Types en Intercom.
                </td></tr>
              ) : (
                status.ticketTypes.map((t) => (
                  <tr key={t.id} className={`hover:bg-gray-50 ${!t.active ? 'opacity-50' : ''}`}>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{t.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{t.name}</td>
                    <td className="px-4 py-3">
                      {t.productKey
                        ? <Badge color="blue" size="sm">{t.productKey}</Badge>
                        : <span className="text-gray-400 text-xs">sin mapeo</span>}
                    </td>
                    <td className="px-4 py-3">
                      <Badge color={t.active ? 'green' : 'gray'} size="sm">
                        {t.archived ? 'archivado' : t.active ? 'activo' : 'eliminado'}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Teams table */}
      {status.teams.length > 0 && (
        <Card>
          <CardHeader><h2 className="font-semibold text-gray-900">Teams / Inboxes</h2></CardHeader>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {status.teams.map((t) => (
              <div key={t.id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2">
                <span className="text-sm font-medium text-gray-800">{t.name}</span>
                <span className="font-mono text-xs text-gray-400">{t.id}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Sync history */}
      {history.length > 0 && (
        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Historial de sincronizaciones</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {history.map((log) => (
              <div key={log.id} className="px-6 py-4">
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                >
                  <div className="flex items-center gap-3">
                    <Badge color={log.status === 'success' ? 'green' : log.status === 'error' ? 'red' : 'yellow'} size="sm">
                      {log.status}
                    </Badge>
                    <span className="text-sm text-gray-700">{formatDate(log.startedAt)}</span>
                    <span className="text-xs text-gray-500">via {log.triggeredBy}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    {log.changesCount > 0 && (
                      <span className="text-loggro-600 font-medium">{log.changesCount} cambio(s)</span>
                    )}
                    <span className="text-gray-400">{formatDuration(log.durationMs)}</span>
                    <span className="text-gray-400 text-xs">{expandedLog === log.id ? '▲' : '▼'}</span>
                  </div>
                </div>

                {expandedLog === log.id && (
                  <div className="mt-3">
                    {log.error && (
                      <div className="rounded bg-red-50 border border-red-200 p-3 text-xs text-red-700 mb-2">{log.error}</div>
                    )}
                    {log.changes.length > 0 ? (
                      <div className="rounded bg-gray-50 border border-gray-200 p-3 space-y-1">
                        {log.changes.map((c, i) => (
                          <div key={i} className="text-xs text-gray-700">
                            <span className="mr-1">{CHANGE_ICONS[c.kind] ?? '•'}</span>
                            <span className="font-medium">{c.name}</span>
                            {c.detail && <span className="text-gray-500"> — {c.detail}</span>}
                            <span className="text-gray-400 ml-1">[{c.kind}]</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500">Sin cambios detectados.</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

// ─── Main Admin page ─────────────────────────────────────────────────────────

export function Admin() {
  const [apiKey, setApiKey] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');
  const [activeTab, setActiveTab] = useState<'stats' | 'config' | 'history' | 'intercom'>('stats');

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
    setConfig({ ...config, products: config.products.map((p) => p.id === id ? { ...p, active: !p.active } : p) });
  };

  const toggleRequestType = (id: string) => {
    if (!config) return;
    setConfig({ ...config, requestTypes: config.requestTypes.map((r) => r.id === id ? { ...r, active: !r.active } : r) });
  };

  const updateTicketTypeId = (productId: string, value: string) => {
    if (!config) return;
    setConfig({ ...config, products: config.products.map((p) => p.id === productId ? { ...p, intercomTicketTypeId: value } : p) });
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

  const TABS = [
    { id: 'stats',    label: 'Estadísticas' },
    { id: 'config',   label: 'Configuración' },
    { id: 'history',  label: 'Historial' },
    { id: 'intercom', label: '🔗 Intercom Sync' },
  ] as const;

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
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit flex-wrap">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.id ? 'bg-white shadow text-gray-900' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'intercom' ? (
        <IntercomSyncPanel apiKey={apiKey} />
      ) : loading ? (
        <div className="flex justify-center py-16"><Spinner text="Cargando..." /></div>
      ) : error ? (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">{error}</div>
      ) : (
        <>
          {/* Stats */}
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

          {/* Config */}
          {activeTab === 'config' && config && (
            <div className="flex flex-col gap-6 animate-fade-in">
              <Card>
                <CardHeader>
                  <h2 className="font-semibold text-gray-900">Productos activos</h2>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Los Ticket Type IDs se sincronizan automáticamente vía <strong>Intercom Sync</strong>.
                    Edita manualmente solo si necesitas sobrescribir.
                  </p>
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
                        label="Intercom Ticket Type ID (auto-sincronizado)"
                        value={p.intercomTicketTypeId}
                        onChange={(e) => updateTicketTypeId(p.id, e.target.value)}
                        placeholder="Se completa automáticamente con Intercom Sync"
                        hint={p.intercomTicketTypeId ? '✅ Mapeado por sync' : '⚠️ Sin mapeo — ejecuta Intercom Sync'}
                      />
                    </div>
                  ))}
                </div>
              </Card>

              <Card>
                <CardHeader><h2 className="font-semibold text-gray-900">Tipos de solicitud</h2></CardHeader>
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

          {/* History */}
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
                          <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{new Date(r.created_at).toLocaleDateString('es-CO')}</td>
                          <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{r.requester_name}</td>
                          <td className="px-4 py-3 text-gray-600">{r.company_name || '—'}</td>
                          <td className="px-4 py-3"><Badge color="blue" size="sm">{r.product}</Badge></td>
                          <td className="px-4 py-3"><Badge color={PRIORITY_COLORS[r.priority] || 'gray'} size="sm">{r.priority}</Badge></td>
                          <td className="px-4 py-3 font-mono text-xs text-gray-600">{r.intercom_ticket_id ? `#${r.intercom_ticket_id}` : '—'}</td>
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
