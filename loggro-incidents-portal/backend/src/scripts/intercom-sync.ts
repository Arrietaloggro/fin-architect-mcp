/**
 * npm run intercom:sync
 *
 * Queries Intercom and updates SQLite with any changes.
 * Also auto-generates .env entries for non-Intercom settings.
 */

import 'dotenv/config';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import { runMigrations } from '../database/migrations';
import { runIntercomSync } from '../services/intercomDiscovery';

const TOKEN = process.env.INTERCOM_ACCESS_TOKEN;
if (!TOKEN) {
  console.error('\n❌ INTERCOM_ACCESS_TOKEN is not set in .env or environment.');
  console.error('   Create the .env file:\n     echo "INTERCOM_ACCESS_TOKEN=<token>" > .env\n');
  process.exit(1);
}

// ─── Ensure .env has required non-Intercom vars ───────────────────────────────

function readEnv(p: string): Record<string, string> {
  if (!fs.existsSync(p)) return {};
  const env: Record<string, string> = {};
  for (const line of fs.readFileSync(p, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const eq = t.indexOf('=');
    if (eq === -1) continue;
    env[t.slice(0, eq).trim()] = t.slice(eq + 1).trim();
  }
  return env;
}

function writeEnv(p: string, env: Record<string, string>): void {
  const sections: Array<{ header: string; keys: string[] }> = [
    {
      header: '# ── Server ──────────────────────────────────────────────────────',
      keys: ['NODE_ENV', 'PORT', 'CORS_ORIGIN', 'LOG_LEVEL'],
    },
    {
      header: '# ── Security ────────────────────────────────────────────────────',
      keys: ['CSRF_SECRET', 'ADMIN_API_KEY', 'ALLOWED_EMAIL_DOMAIN'],
    },
    {
      header: '# ── Intercom ─────────────────────────────────────────────────────',
      keys: Object.keys(env).filter((k) => k.startsWith('INTERCOM')),
    },
    {
      header: '# ── Database ────────────────────────────────────────────────────',
      keys: ['DATABASE_PATH'],
    },
    {
      header: '# ── Uploads ─────────────────────────────────────────────────────',
      keys: ['MAX_FILE_SIZE_MB', 'MAX_FILES_PER_REQUEST', 'ALLOWED_FILE_TYPES'],
    },
    {
      header: '# ── Rate limiting ───────────────────────────────────────────────',
      keys: ['RATE_LIMIT_WINDOW_MS', 'RATE_LIMIT_MAX_REQUESTS'],
    },
  ];

  const lines = [
    '# Loggro Incidents Portal — generated/updated by intercom:sync',
    `# Updated: ${new Date().toISOString()}`,
    '',
  ];
  const written = new Set<string>();

  for (const section of sections) {
    const relevant = section.keys.filter((k) => k in env);
    if (!relevant.length) continue;
    lines.push(section.header);
    for (const k of relevant) {
      lines.push(`${k}=${env[k]}`);
      written.add(k);
    }
    lines.push('');
  }

  const leftover = Object.keys(env).filter((k) => !written.has(k));
  if (leftover.length) {
    for (const k of leftover) lines.push(`${k}=${env[k]}`);
    lines.push('');
  }

  fs.writeFileSync(p, lines.join('\n'));
}

function generateHex(bytes: number): string {
  return crypto.randomBytes(bytes).toString('hex');
}

async function main() {
  console.log('\n🔄 Loggro Incidents Portal — Intercom Sync\n');
  console.log('═'.repeat(60));

  const ENV_PATH = path.resolve(__dirname, '../../.env');
  const env = readEnv(ENV_PATH);
  env['INTERCOM_ACCESS_TOKEN'] = TOKEN!;

  // Ensure critical non-Intercom defaults
  if (!env['NODE_ENV'])               env['NODE_ENV'] = 'development';
  if (!env['PORT'])                   env['PORT'] = '3001';
  if (!env['CORS_ORIGIN'])            env['CORS_ORIGIN'] = 'http://localhost:5173';
  if (!env['LOG_LEVEL'])              env['LOG_LEVEL'] = 'info';
  if (!env['ALLOWED_EMAIL_DOMAIN'])   env['ALLOWED_EMAIL_DOMAIN'] = 'loggro.com';
  if (!env['DATABASE_PATH'])          env['DATABASE_PATH'] = './data/portal.db';
  if (!env['MAX_FILE_SIZE_MB'])       env['MAX_FILE_SIZE_MB'] = '10';
  if (!env['MAX_FILES_PER_REQUEST'])  env['MAX_FILES_PER_REQUEST'] = '5';
  if (!env['RATE_LIMIT_WINDOW_MS'])   env['RATE_LIMIT_WINDOW_MS'] = '900000';
  if (!env['RATE_LIMIT_MAX_REQUESTS']) env['RATE_LIMIT_MAX_REQUESTS'] = '5';
  if (!env['INTERCOM_API_VERSION'])   env['INTERCOM_API_VERSION'] = '2.11';

  const defaultCsrf  = 'dev-csrf-secret-change-in-production-min32chars!!';
  const defaultAdmin = 'dev-admin-key-change-in-production';
  if (!env['CSRF_SECRET'] || env['CSRF_SECRET'] === defaultCsrf) {
    env['CSRF_SECRET'] = generateHex(32);
    console.log('🔑 Generated new CSRF_SECRET');
  }
  if (!env['ADMIN_API_KEY'] || env['ADMIN_API_KEY'] === defaultAdmin) {
    env['ADMIN_API_KEY'] = generateHex(24);
    console.log(`🔑 Generated new ADMIN_API_KEY: ${env['ADMIN_API_KEY']}`);
  }

  // Ensure DB directory exists and run migrations
  const dbPath = path.resolve(env['DATABASE_PATH']);
  const dbDir = path.dirname(dbPath);
  if (!fs.existsSync(dbDir)) fs.mkdirSync(dbDir, { recursive: true });

  console.log('\n📦 Running DB migrations…');
  process.env['DATABASE_PATH'] = dbPath;
  runMigrations();
  console.log('   ✅ Schema ready');

  // Run sync
  console.log('\n🔍 Syncing with Intercom…\n');
  const result = await runIntercomSync(TOKEN!, 'manual');

  // Print results
  if (result.workspace) {
    console.log(`🏢 Workspace: ${result.workspace.name} (${result.workspace.id})`);
    console.log(`   Region: ${result.workspace.region} | Timezone: ${result.workspace.timezone}`);
  }

  console.log(`\n🎫 Ticket Types: ${result.ticketTypes.filter((t) => !t.archived).length} active`);
  const mapped: string[] = [];
  const unmapped: string[] = [];
  for (const tt of result.ticketTypes.filter((t) => !t.archived)) {
    const db = (await import('../database/connection')).getDb();
    const row = db.prepare('SELECT product_key FROM intercom_ticket_types WHERE id = ?').get(tt.id) as { product_key: string | null } | undefined;
    if (row?.product_key) {
      mapped.push(`   ✅ ${tt.name} (${tt.id}) → ${row.product_key}`);
    } else {
      unmapped.push(`   ❓ ${tt.name} (${tt.id}) → sin producto mapeado`);
    }
  }
  mapped.forEach((l) => console.log(l));
  unmapped.forEach((l) => console.log(l));

  console.log(`\n👥 Teams: ${result.teams.length}`);
  result.teams.forEach((t) => console.log(`   • ${t.name} (${t.id})`));

  console.log(`\n👤 Admins: ${result.admins.length}`);
  result.admins.forEach((a) => console.log(`   • ${a.name} <${a.email}>`));

  // Changes summary
  if (result.changes.length > 0) {
    console.log(`\n📋 Cambios detectados (${result.changes.length}):`);
    for (const c of result.changes) {
      const icon: Record<string, string> = {
        ticket_type_added: '➕', ticket_type_deleted: '🗑 ', ticket_type_renamed: '✏️ ',
        ticket_type_product_mapped: '🔗', ticket_type_attributes_changed: '📎',
        team_added: '➕', team_deleted: '🗑 ', team_renamed: '✏️ ',
        admin_added: '➕', admin_deleted: '🗑 ',
        custom_attr_added: '➕', custom_attr_deleted: '🗑 ',
        workspace_updated: '🔄',
      };
      console.log(`   ${icon[c.kind] ?? '•'} [${c.kind}] ${c.name}${c.detail ? ` — ${c.detail}` : ''}`);
    }
  } else {
    console.log('\n✅ Sin cambios — todo está actualizado');
  }

  // Write .env
  writeEnv(ENV_PATH, env);
  console.log(`\n📄 .env actualizado: ${ENV_PATH}`);

  // Exit
  console.log('\n' + '═'.repeat(60));
  if (result.status === 'success') {
    console.log(`\n✅ Sync completado en ${result.durationMs}ms (log ID: ${result.logId})\n`);
    process.exit(0);
  } else {
    console.error(`\n❌ Sync falló: ${result.error}\n`);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('\n❌ Fatal error:', err.message);
  process.exit(1);
});
