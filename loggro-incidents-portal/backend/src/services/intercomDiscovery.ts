/**
 * intercomDiscovery — shared service used by:
 *  - npm run intercom:sync  (CLI)
 *  - POST /admin/intercom/sync  (API)
 *  - startup auto-sync
 *
 * Discovers all Intercom workspace configuration, diffs against the current
 * SQLite state, persists changes, and returns a structured change report.
 */

import axios, { AxiosInstance } from 'axios';
import { getDb } from '../database/connection';
import { logger } from '../utils/logger';

// ─── Intercom API types ───────────────────────────────────────────────────────

export interface IcTicketType {
  id: string;
  name: string;
  description: string;
  icon: string;
  archived: boolean;
  ticket_type_attributes?: { data?: IcTicketAttribute[] } | IcTicketAttribute[];
}

export interface IcTicketAttribute {
  id: string;
  name: string;
  data_type: string;
  required_to_create: boolean;
  required_to_create_for_contacts: boolean;
  description?: string;
  allowed_values?: string[];
}

export interface IcTeam {
  id: string;
  name: string;
}

export interface IcAdmin {
  id: string;
  name: string;
  email: string;
}

export interface IcCustomAttribute {
  id: string;
  name: string;
  full_name: string;
  label: string;
  data_type: string;
  description?: string;
  options?: Array<{ value: string }>;
}

// ─── Change types ────────────────────────────────────────────────────────────

export type ChangeKind =
  | 'ticket_type_added'
  | 'ticket_type_deleted'
  | 'ticket_type_renamed'
  | 'ticket_type_product_mapped'
  | 'ticket_type_attributes_changed'
  | 'team_added'
  | 'team_deleted'
  | 'team_renamed'
  | 'admin_added'
  | 'admin_deleted'
  | 'custom_attr_added'
  | 'custom_attr_deleted'
  | 'workspace_updated';

export interface SyncChange {
  kind: ChangeKind;
  id: string;
  name: string;
  detail?: string;
}

export interface SyncResult {
  logId: number;
  status: 'success' | 'error';
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  changes: SyncChange[];
  ticketTypes: IcTicketType[];
  teams: IcTeam[];
  admins: IcAdmin[];
  workspace: { id: string; name: string; region: string; timezone: string } | null;
  error?: string;
}

// ─── Product keyword matcher ─────────────────────────────────────────────────

const PRODUCT_KEYWORDS: Record<string, string[]> = {
  'erp-pymes':    ['erp', 'pymes', 'pyme'],
  'restobar':     ['restobar', 'resto', 'bar', 'restaurante', 'restaurant'],
  'pos-tienda':   ['pos', 'tienda', 'punto de venta', 'store', 'retail'],
  'nomina':       ['nomina', 'nómina', 'payroll', 'rrhh'],
  'alojamientos': ['alojamiento', 'hotel', 'hospedaje', 'accommodation'],
  'enterprise':   ['enterprise', 'empresarial', 'corporativo'],
};

function matchProduct(name: string, description = ''): string | null {
  const text = `${name} ${description}`.toLowerCase();
  for (const [product, keywords] of Object.entries(PRODUCT_KEYWORDS)) {
    if (keywords.some((kw) => text.includes(kw))) return product;
  }
  return null;
}

// ─── Intercom API client factory ─────────────────────────────────────────────

function makeClient(token: string): AxiosInstance {
  return axios.create({
    baseURL: 'https://api.intercom.io',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'Intercom-Version': '2.11',
    },
    timeout: 20_000,
  });
}

// ─── Fetch helpers ────────────────────────────────────────────────────────────

async function fetchWorkspace(api: AxiosInstance) {
  const res = await api.get('/me');
  const d = res.data;
  return {
    id: String(d.app?.app_id ?? d.app_id ?? d.id ?? ''),
    name: String(d.app?.name ?? d.name ?? ''),
    region: String(d.app?.region ?? d.region ?? ''),
    timezone: String(d.app?.timezone ?? d.timezone ?? ''),
    raw: d,
  };
}

async function fetchTicketTypes(api: AxiosInstance): Promise<IcTicketType[]> {
  const res = await api.get('/ticket_types');
  return res.data.data ?? res.data.ticket_types ?? [];
}

async function fetchTicketAttributes(api: AxiosInstance, id: string): Promise<IcTicketAttribute[]> {
  try {
    const res = await api.get(`/ticket_types/${id}`);
    const attrs = res.data.ticket_type_attributes;
    if (!attrs) return [];
    if (Array.isArray(attrs)) return attrs;
    return attrs.data ?? [];
  } catch {
    return [];
  }
}

async function fetchTeams(api: AxiosInstance): Promise<IcTeam[]> {
  try {
    const res = await api.get('/teams');
    return res.data.teams ?? [];
  } catch {
    return [];
  }
}

async function fetchAdmins(api: AxiosInstance): Promise<IcAdmin[]> {
  try {
    const res = await api.get('/admins');
    return res.data.admins ?? [];
  } catch {
    return [];
  }
}

async function fetchCustomAttributes(
  api: AxiosInstance,
  model: 'conversation' | 'contact'
): Promise<IcCustomAttribute[]> {
  try {
    const res = await api.get(`/data_attributes?model=${model}`);
    return (res.data.data ?? []).filter((a: IcCustomAttribute) =>
      a.full_name?.startsWith('custom_attributes.')
    );
  } catch {
    return [];
  }
}

// ─── DB helpers ──────────────────────────────────────────────────────────────

function now(): string {
  return new Date().toISOString();
}

function upsertTicketType(
  db: ReturnType<typeof getDb>,
  tt: IcTicketType,
  attrs: IcTicketAttribute[]
): SyncChange[] {
  const changes: SyncChange[] = [];
  const existing = db
    .prepare('SELECT id, name, product_key, attributes_json, deleted_at FROM intercom_ticket_types WHERE id = ?')
    .get(tt.id) as { id: string; name: string; product_key: string | null; attributes_json: string | null; deleted_at: string | null } | undefined;

  const productKey = matchProduct(tt.name, tt.description);
  const attrsJson = JSON.stringify(attrs);

  if (!existing) {
    db.prepare(`
      INSERT INTO intercom_ticket_types
        (id, name, description, icon, archived, product_key, attributes_json, raw_json, first_seen_at, last_seen_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      tt.id, tt.name, tt.description, tt.icon,
      tt.archived ? 1 : 0, productKey,
      attrsJson, JSON.stringify(tt), now(), now()
    );
    changes.push({ kind: 'ticket_type_added', id: tt.id, name: tt.name, detail: productKey ? `→ ${productKey}` : 'sin mapeo de producto' });
    if (productKey) {
      changes.push({ kind: 'ticket_type_product_mapped', id: tt.id, name: tt.name, detail: productKey });
    }
  } else {
    const updates: string[] = [];
    const params: unknown[] = [];

    if (existing.deleted_at) {
      updates.push('deleted_at = NULL');
      changes.push({ kind: 'ticket_type_added', id: tt.id, name: tt.name, detail: 'restaurado (estaba eliminado)' });
    }
    if (existing.name !== tt.name) {
      updates.push('name = ?'); params.push(tt.name);
      changes.push({ kind: 'ticket_type_renamed', id: tt.id, name: tt.name, detail: `antes: "${existing.name}"` });
    }
    if (existing.product_key !== productKey && productKey) {
      updates.push('product_key = ?'); params.push(productKey);
      if (!existing.product_key) {
        changes.push({ kind: 'ticket_type_product_mapped', id: tt.id, name: tt.name, detail: productKey });
      }
    }
    if (existing.attributes_json !== attrsJson) {
      updates.push('attributes_json = ?'); params.push(attrsJson);
      changes.push({ kind: 'ticket_type_attributes_changed', id: tt.id, name: tt.name, detail: `${attrs.length} atributos` });
    }
    updates.push('archived = ?', 'raw_json = ?', 'last_seen_at = ?');
    params.push(tt.archived ? 1 : 0, JSON.stringify(tt), now());

    if (updates.length > 3 || existing.deleted_at) {
      db.prepare(`UPDATE intercom_ticket_types SET ${updates.join(', ')} WHERE id = ?`)
        .run(...params, tt.id);
    } else {
      db.prepare('UPDATE intercom_ticket_types SET archived = ?, raw_json = ?, last_seen_at = ? WHERE id = ?')
        .run(tt.archived ? 1 : 0, JSON.stringify(tt), now(), tt.id);
    }
  }
  return changes;
}

function upsertTeam(db: ReturnType<typeof getDb>, team: IcTeam): SyncChange[] {
  const changes: SyncChange[] = [];
  const existing = db
    .prepare('SELECT id, name, deleted_at FROM intercom_teams WHERE id = ?')
    .get(team.id) as { id: string; name: string; deleted_at: string | null } | undefined;

  if (!existing) {
    db.prepare('INSERT INTO intercom_teams (id, name, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?)')
      .run(team.id, team.name, JSON.stringify(team), now(), now());
    changes.push({ kind: 'team_added', id: team.id, name: team.name });
  } else {
    if (existing.deleted_at) {
      db.prepare('UPDATE intercom_teams SET deleted_at = NULL, name = ?, last_seen_at = ? WHERE id = ?')
        .run(team.name, now(), team.id);
      changes.push({ kind: 'team_added', id: team.id, name: team.name, detail: 'restaurado' });
    } else if (existing.name !== team.name) {
      db.prepare('UPDATE intercom_teams SET name = ?, raw_json = ?, last_seen_at = ? WHERE id = ?')
        .run(team.name, JSON.stringify(team), now(), team.id);
      changes.push({ kind: 'team_renamed', id: team.id, name: team.name, detail: `antes: "${existing.name}"` });
    } else {
      db.prepare('UPDATE intercom_teams SET last_seen_at = ? WHERE id = ?').run(now(), team.id);
    }
  }
  return changes;
}

function upsertAdmin(
  db: ReturnType<typeof getDb>,
  admin: IcAdmin,
  tokenOwnerId: string
): SyncChange[] {
  const changes: SyncChange[] = [];
  const isOwner = admin.id === tokenOwnerId ? 1 : 0;
  const existing = db
    .prepare('SELECT id, deleted_at FROM intercom_admins WHERE id = ?')
    .get(admin.id) as { id: string; deleted_at: string | null } | undefined;

  if (!existing) {
    db.prepare('INSERT INTO intercom_admins (id, name, email, is_token_owner, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
      .run(admin.id, admin.name, admin.email, isOwner, JSON.stringify(admin), now(), now());
    changes.push({ kind: 'admin_added', id: admin.id, name: `${admin.name} <${admin.email}>` });
  } else {
    db.prepare('UPDATE intercom_admins SET name = ?, email = ?, is_token_owner = ?, raw_json = ?, deleted_at = NULL, last_seen_at = ? WHERE id = ?')
      .run(admin.name, admin.email, isOwner, JSON.stringify(admin), now(), admin.id);
  }
  return changes;
}

function upsertCustomAttribute(
  db: ReturnType<typeof getDb>,
  attr: IcCustomAttribute,
  model: string
): SyncChange[] {
  const changes: SyncChange[] = [];
  const existing = db
    .prepare('SELECT id, deleted_at FROM intercom_custom_attributes WHERE id = ?')
    .get(attr.id) as { id: string; deleted_at: string | null } | undefined;

  const optionsJson = attr.options ? JSON.stringify(attr.options.map((o) => o.value)) : null;

  if (!existing) {
    db.prepare(`
      INSERT INTO intercom_custom_attributes
        (id, model, name, full_name, label, data_type, description, options_json, raw_json, first_seen_at, last_seen_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(attr.id, model, attr.name, attr.full_name, attr.label, attr.data_type,
           attr.description ?? null, optionsJson, JSON.stringify(attr), now(), now());
    changes.push({ kind: 'custom_attr_added', id: attr.id, name: `[${model}] ${attr.label}`, detail: attr.data_type });
  } else {
    db.prepare('UPDATE intercom_custom_attributes SET name = ?, label = ?, data_type = ?, options_json = ?, raw_json = ?, deleted_at = NULL, last_seen_at = ? WHERE id = ?')
      .run(attr.name, attr.label, attr.data_type, optionsJson, JSON.stringify(attr), now(), attr.id);
  }
  return changes;
}

function markDeletedNotSeen(
  db: ReturnType<typeof getDb>,
  table: string,
  seenIds: string[],
  changeKind: ChangeKind
): SyncChange[] {
  const changes: SyncChange[] = [];
  const placeholders = seenIds.length ? seenIds.map(() => '?').join(',') : "'__never__'";
  const rows = db.prepare(
    `SELECT id, name FROM ${table} WHERE deleted_at IS NULL AND id NOT IN (${placeholders})`
  ).all(...seenIds) as Array<{ id: string; name: string }>;

  for (const row of rows) {
    db.prepare(`UPDATE ${table} SET deleted_at = ? WHERE id = ?`).run(now(), row.id);
    changes.push({ kind: changeKind, id: row.id, name: row.name });
  }
  return changes;
}

// ─── Main sync function ───────────────────────────────────────────────────────

export async function runIntercomSync(
  token: string,
  triggeredBy: 'manual' | 'startup' | 'api' = 'manual'
): Promise<SyncResult> {
  const db = getDb();
  const startedAt = now();
  const startMs = Date.now();

  // Create log entry
  const logResult = db.prepare(
    "INSERT INTO intercom_sync_log (started_at, status, triggered_by) VALUES (?, 'running', ?)"
  ).run(startedAt, triggeredBy);
  const logId = logResult.lastInsertRowid as number;

  const allChanges: SyncChange[] = [];
  let fetchedTicketTypes: IcTicketType[] = [];
  let fetchedTeams: IcTeam[] = [];
  let fetchedAdmins: IcAdmin[] = [];
  let fetchedWorkspace: { id: string; name: string; region: string; timezone: string } | null = null;

  try {
    const api = makeClient(token);

    // ── Validate token ──────────────────────────────────────────────────────
    logger.info('Intercom sync: validating token', { logId });
    const meRes = await api.get('/me');
    const tokenOwnerAdminId = String(meRes.data.id ?? '');
    const wsData = meRes.data;

    // ── Workspace ───────────────────────────────────────────────────────────
    fetchedWorkspace = {
      id: String(wsData.app?.app_id ?? wsData.app_id ?? wsData.id ?? ''),
      name: String(wsData.app?.name ?? wsData.name ?? ''),
      region: String(wsData.app?.region ?? wsData.region ?? ''),
      timezone: String(wsData.app?.timezone ?? wsData.timezone ?? ''),
    };

    const lastWs = db.prepare('SELECT workspace_id, name FROM intercom_workspace ORDER BY id DESC LIMIT 1')
      .get() as { workspace_id: string; name: string } | undefined;

    if (!lastWs || lastWs.workspace_id !== fetchedWorkspace.id || lastWs.name !== fetchedWorkspace.name) {
      db.prepare('INSERT INTO intercom_workspace (workspace_id, name, region, timezone, raw_json, synced_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(fetchedWorkspace.id, fetchedWorkspace.name, fetchedWorkspace.region, fetchedWorkspace.timezone, JSON.stringify(wsData), now());
      if (lastWs) {
        allChanges.push({ kind: 'workspace_updated', id: fetchedWorkspace.id, name: fetchedWorkspace.name });
      }
    } else {
      db.prepare('UPDATE intercom_workspace SET synced_at = ? WHERE workspace_id = ?')
        .run(now(), fetchedWorkspace.id);
    }

    // ── Ticket Types ────────────────────────────────────────────────────────
    logger.info('Intercom sync: fetching ticket types', { logId });
    fetchedTicketTypes = await fetchTicketTypes(api);

    for (const tt of fetchedTicketTypes) {
      const attrs = await fetchTicketAttributes(api, tt.id);
      const changes = upsertTicketType(db, tt, attrs);
      allChanges.push(...changes);
    }
    // Mark deleted
    const seenTtIds = fetchedTicketTypes.map((t) => t.id);
    allChanges.push(...markDeletedNotSeen(db, 'intercom_ticket_types', seenTtIds, 'ticket_type_deleted'));

    // Sync active ticket type IDs back into portal_config.products
    syncTicketTypesToPortalConfig(db);

    // ── Teams ───────────────────────────────────────────────────────────────
    logger.info('Intercom sync: fetching teams', { logId });
    fetchedTeams = await fetchTeams(api);

    for (const team of fetchedTeams) {
      allChanges.push(...upsertTeam(db, team));
    }
    const seenTeamIds = fetchedTeams.map((t) => t.id);
    allChanges.push(...markDeletedNotSeen(db, 'intercom_teams', seenTeamIds, 'team_deleted'));

    // ── Admins ──────────────────────────────────────────────────────────────
    logger.info('Intercom sync: fetching admins', { logId });
    fetchedAdmins = await fetchAdmins(api);

    for (const admin of fetchedAdmins) {
      allChanges.push(...upsertAdmin(db, admin, tokenOwnerAdminId));
    }
    const seenAdminIds = fetchedAdmins.map((a) => a.id);
    allChanges.push(...markDeletedNotSeen(db, 'intercom_admins', seenAdminIds, 'admin_deleted'));

    // ── Custom Attributes ───────────────────────────────────────────────────
    logger.info('Intercom sync: fetching custom attributes', { logId });
    const convAttrs = await fetchCustomAttributes(api, 'conversation');
    const contactAttrs = await fetchCustomAttributes(api, 'contact');

    for (const attr of convAttrs) allChanges.push(...upsertCustomAttribute(db, attr, 'conversation'));
    for (const attr of contactAttrs) allChanges.push(...upsertCustomAttribute(db, attr, 'contact'));

    const seenAttrIds = [...convAttrs, ...contactAttrs].map((a) => a.id);
    allChanges.push(...markDeletedNotSeen(db, 'intercom_custom_attributes', seenAttrIds, 'custom_attr_deleted'));

    // ── Finalize log ────────────────────────────────────────────────────────
    const finishedAt = now();
    const durationMs = Date.now() - startMs;
    db.prepare('UPDATE intercom_sync_log SET finished_at = ?, status = ?, changes_json = ?, duration_ms = ? WHERE id = ?')
      .run(finishedAt, 'success', JSON.stringify(allChanges), durationMs, logId);

    logger.info('Intercom sync completed', { logId, changes: allChanges.length, durationMs });

    return {
      logId,
      status: 'success',
      startedAt,
      finishedAt,
      durationMs,
      changes: allChanges,
      ticketTypes: fetchedTicketTypes,
      teams: fetchedTeams,
      admins: fetchedAdmins,
      workspace: fetchedWorkspace,
    };
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    const finishedAt = now();
    const durationMs = Date.now() - startMs;

    db.prepare('UPDATE intercom_sync_log SET finished_at = ?, status = ?, error_message = ?, changes_json = ?, duration_ms = ? WHERE id = ?')
      .run(finishedAt, 'error', errorMessage, JSON.stringify(allChanges), durationMs, logId);

    logger.error('Intercom sync failed', { logId, error: errorMessage });

    return {
      logId,
      status: 'error',
      startedAt,
      finishedAt,
      durationMs,
      changes: allChanges,
      ticketTypes: fetchedTicketTypes,
      teams: fetchedTeams,
      admins: fetchedAdmins,
      workspace: fetchedWorkspace,
      error: errorMessage,
    };
  }
}

// ─── Sync ticket type IDs back into portal_config ────────────────────────────

function syncTicketTypesToPortalConfig(db: ReturnType<typeof getDb>): void {
  const row = db.prepare("SELECT config_value FROM portal_config WHERE config_key = 'main'").get() as
    | { config_value: string }
    | undefined;
  if (!row) return;

  let cfg: { products?: Array<{ id: string; intercomTicketTypeId?: string }> };
  try {
    cfg = JSON.parse(row.config_value);
  } catch {
    return;
  }

  if (!Array.isArray(cfg.products)) return;

  const ticketTypes = db.prepare(
    "SELECT id, product_key FROM intercom_ticket_types WHERE deleted_at IS NULL AND archived = 0 AND product_key IS NOT NULL"
  ).all() as Array<{ id: string; product_key: string }>;

  const byProduct = new Map(ticketTypes.map((t) => [t.product_key, t.id]));
  let changed = false;

  for (const product of cfg.products) {
    const intercomId = byProduct.get(product.id);
    if (intercomId && product.intercomTicketTypeId !== intercomId) {
      product.intercomTicketTypeId = intercomId;
      changed = true;
    }
  }

  if (changed) {
    db.prepare("UPDATE portal_config SET config_value = ?, updated_at = ? WHERE config_key = 'main'")
      .run(JSON.stringify(cfg), now());
    logger.info('Portal config: ticket type IDs updated from Intercom sync');
  }
}

// ─── Query helpers used by API endpoints ─────────────────────────────────────

export function getLatestSyncStatus() {
  const db = getDb();
  const log = db.prepare(
    'SELECT * FROM intercom_sync_log ORDER BY id DESC LIMIT 1'
  ).get() as {
    id: number; started_at: string; finished_at: string | null; status: string;
    triggered_by: string; changes_json: string | null; error_message: string | null; duration_ms: number | null;
  } | undefined;

  if (!log) return null;

  const ticketTypes = db.prepare(
    'SELECT id, name, product_key, archived, deleted_at FROM intercom_ticket_types ORDER BY name'
  ).all() as Array<{ id: string; name: string; product_key: string | null; archived: number; deleted_at: string | null }>;

  const teams = db.prepare(
    'SELECT id, name, deleted_at FROM intercom_teams ORDER BY name'
  ).all() as Array<{ id: string; name: string; deleted_at: string | null }>;

  const workspace = db.prepare(
    'SELECT workspace_id, name, region, timezone, synced_at FROM intercom_workspace ORDER BY id DESC LIMIT 1'
  ).get() as { workspace_id: string; name: string; region: string; timezone: string; synced_at: string } | undefined;

  return {
    lastSync: {
      id: log.id,
      startedAt: log.started_at,
      finishedAt: log.finished_at,
      status: log.status,
      triggeredBy: log.triggered_by,
      durationMs: log.duration_ms,
      changesCount: log.changes_json ? (JSON.parse(log.changes_json) as unknown[]).length : 0,
      changes: log.changes_json ? JSON.parse(log.changes_json) : [],
      error: log.error_message,
    },
    workspace: workspace ?? null,
    ticketTypes: ticketTypes.map((t) => ({
      id: t.id,
      name: t.name,
      productKey: t.product_key,
      archived: t.archived === 1,
      active: t.deleted_at === null && t.archived === 0,
    })),
    teams: teams
      .filter((t) => t.deleted_at === null)
      .map((t) => ({ id: t.id, name: t.name })),
  };
}

export function getSyncHistory(limit = 20) {
  const db = getDb();
  return db.prepare(
    'SELECT id, started_at, finished_at, status, triggered_by, changes_json, error_message, duration_ms FROM intercom_sync_log ORDER BY id DESC LIMIT ?'
  ).all(limit) as Array<{
    id: number; started_at: string; finished_at: string | null; status: string;
    triggered_by: string; changes_json: string | null; error_message: string | null; duration_ms: number | null;
  }>;
}

export function getTicketTypeIdForProduct(productKey: string): string | null {
  const db = getDb();
  const row = db.prepare(
    "SELECT id FROM intercom_ticket_types WHERE product_key = ? AND deleted_at IS NULL AND archived = 0 LIMIT 1"
  ).get(productKey) as { id: string } | undefined;
  return row?.id ?? null;
}
