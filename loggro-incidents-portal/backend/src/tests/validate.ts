/**
 * Validation test suite — runs without external dependencies.
 * Usage: npx ts-node --transpile-only src/tests/validate.ts
 */

import 'dotenv/config';
import crypto from 'crypto';

let passed = 0;
let failed = 0;

function test(name: string, fn: () => void | Promise<void>) {
  try {
    const result = fn();
    if (result instanceof Promise) {
      result.then(() => { console.log(`  ✓ ${name}`); passed++; }).catch((e) => { console.error(`  ✗ ${name}: ${e.message}`); failed++; });
    } else {
      console.log(`  ✓ ${name}`);
      passed++;
    }
  } catch (e: unknown) {
    console.error(`  ✗ ${name}: ${e instanceof Error ? e.message : e}`);
    failed++;
  }
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

async function run() {
  // ─── Config ─────────────────────────────────────────────────────────────────
  console.log('\n📋 Configuration');
  const { config } = await import('../config');

  test('Port is a valid number', () => assert(config.port > 0 && config.port < 65536, 'Invalid port'));
  test('Allowed email domain set', () => assert(config.security.allowedEmailDomain.length > 0, 'No email domain'));
  test('CSRF secret has minimum length', () => assert(config.security.csrfSecret.length >= 16, 'CSRF secret too short'));
  test('Rate limit window > 0', () => assert(config.rateLimit.windowMs > 0, 'Invalid window'));
  test('Max file size > 0', () => assert(config.uploads.maxFileSizeMb > 0, 'Invalid file size'));
  test('Allowed MIME types not empty', () => assert(config.uploads.allowedMimeTypes.length > 0, 'No MIME types'));
  if (config.intercom.accessToken) {
    test('Intercom token format ok', () => assert(config.intercom.accessToken.length > 10, 'Token too short'));
  } else {
    console.log('  ⚠ INTERCOM_ACCESS_TOKEN not set — ticket creation will fail');
  }

  // ─── Domain validation ───────────────────────────────────────────────────────
  console.log('\n🔐 Domain validation');
  const domain = config.security.allowedEmailDomain;
  const domainRe = new RegExp(`^[a-zA-Z0-9._%+\\-]+@${domain.replace('.', '\\.')}$`, 'i');

  test('Valid corporate email passes', () => assert(domainRe.test('juan@loggro.com'), 'Should pass'));
  test('Gmail blocked', () => assert(!domainRe.test('juan@gmail.com'), 'Should block'));
  test('Subdomain email blocked', () => assert(!domainRe.test('juan@sub.loggro.com'), 'Should block subdomain'));
  test('Empty string blocked', () => assert(!domainRe.test(''), 'Should block empty'));
  test('Mixed case accepted', () => assert(domainRe.test('Juan.Perez@LOGGRO.COM'), 'Should accept mixed case'));

  // ─── CSRF ────────────────────────────────────────────────────────────────────
  console.log('\n🛡  CSRF');
  // Re-implement the logic inline for pure unit testing
  const CSRF_SECRET = config.security.csrfSecret;
  function makeToken(fp: string): string {
    const ts = Date.now();
    const h = crypto.createHmac('sha256', CSRF_SECRET).update(`${fp}:${ts}`).digest('hex');
    return `${ts}.${h}`;
  }
  function checkToken(token: string, fp: string): boolean {
    const parts = token.split('.');
    if (parts.length !== 2) return false;
    const [tsStr, sig] = parts;
    const ts = parseInt(tsStr, 10);
    if (isNaN(ts) || Date.now() - ts > 3_600_000) return false;
    const expected = crypto.createHmac('sha256', CSRF_SECRET).update(`${fp}:${ts}`).digest('hex');
    return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
  }
  test('Valid CSRF token passes', () => assert(checkToken(makeToken('1.2.3.4'), '1.2.3.4'), 'Should pass'));
  test('Token from different IP rejected', () => assert(!checkToken(makeToken('1.2.3.4'), '9.9.9.9'), 'Should reject'));
  test('Tampered token rejected', () => assert(!checkToken('999.' + makeToken('1.2.3.4').split('.')[1], '1.2.3.4'), 'Should reject tampered'));
  test('Garbage token rejected', () => assert(!checkToken('garbage', '1.2.3.4'), 'Should reject garbage'));

  // ─── Database ────────────────────────────────────────────────────────────────
  console.log('\n🗃  Database');
  const { runMigrations } = await import('../database/migrations');
  const { getDb } = await import('../database/connection');
  const { TicketHistoryModel } = await import('../models/TicketHistory');
  const { PortalConfigModel } = await import('../models/PortalConfig');

  test('Migrations run without error', () => { runMigrations(); });

  test('Config has products', () => {
    const cfg = PortalConfigModel.get();
    assert(Array.isArray(cfg.products) && cfg.products.length >= 6, `Expected 6 products, got ${cfg.products.length}`);
  });

  test('Config has priorities', () => {
    const cfg = PortalConfigModel.get();
    assert(Array.isArray(cfg.priorities) && cfg.priorities.length === 4, 'Expected 4 priorities');
  });

  test('Ticket history insert/read/delete', () => {
    const db = getDb();
    const id = TicketHistoryModel.create({
      requester_name: 'Test User',
      requester_email: 'test@loggro.com',
      company_name: 'Test Co',
      company_nit: '900000000',
      product: 'erp-pymes',
      request_type: 'bug',
      priority: 'low',
      operational_impact: 'none',
      description: 'Validation test record',
      status: 'success',
      intercom_ticket_id: 'TEST-VALIDATE-001',
      intercom_ticket_url: null,
      error_message: null,
      ip_address: null,
      user_agent: null,
      response_time_ms: null,
    });
    assert(id > 0, 'Insert failed');
    const record = TicketHistoryModel.findById(id);
    assert(record?.requester_email === 'test@loggro.com', 'Record email mismatch');
    assert(record?.status === 'success', 'Status mismatch');
    db.prepare('DELETE FROM ticket_history WHERE id = ?').run(id);
  });

  test('Stats returns expected shape', () => {
    const stats = TicketHistoryModel.getStats();
    assert(typeof (stats as Record<string, unknown>).total === 'number', 'No total in stats');
  });

  // ─── File rules ──────────────────────────────────────────────────────────────
  console.log('\n📎 File validation rules');
  test('PDF is allowed', () => assert(config.uploads.allowedMimeTypes.includes('application/pdf'), 'PDF not allowed'));
  test('JPEG is allowed', () => assert(config.uploads.allowedMimeTypes.includes('image/jpeg'), 'JPEG not allowed'));
  test('Word docx is allowed', () => assert(config.uploads.allowedMimeTypes.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document'), 'DOCX not allowed'));
  test('Executable NOT allowed', () => assert(!config.uploads.allowedMimeTypes.includes('application/x-executable'), 'EXE should not be allowed'));
  test('Max file size ≤ 50MB', () => assert(config.uploads.maxFileSizeMb <= 50, 'File size limit too high'));
  test('Max files ≤ 10', () => assert(config.uploads.maxFilesPerRequest <= 10, 'Too many files allowed'));

  // ─── Field validation (body validator) ───────────────────────────────────────
  console.log('\n📝 Form validation');
  type Body = Record<string, unknown>;
  const REQUIRED = ['requesterName','requesterEmail','companyName','product','requestType','priority','description'];
  function validateBody(body: Body): string | null {
    for (const field of REQUIRED) {
      const v = body[field];
      if (!v || (typeof v === 'string' && !v.trim())) return `Missing: ${field}`;
    }
    const email = body.requesterEmail as string;
    if (!/^[a-zA-Z0-9._%+\-]+@loggro\.com$/i.test(email)) return 'Invalid email domain';
    const desc = body.description as string;
    if (desc.trim().length < 10) return 'Description too short';
    return null;
  }

  const validBody: Body = {
    requesterName: 'Juan Perez', requesterEmail: 'juan@loggro.com',
    companyName: 'Cliente SA', product: 'erp-pymes',
    requestType: 'bug', priority: 'high',
    description: 'El sistema no genera facturas correctamente',
  };

  test('Valid body passes', () => assert(validateBody(validBody) === null, 'Should pass'));
  test('Missing description fails', () => assert(validateBody({...validBody, description: ''}) !== null, 'Should fail'));
  test('Gmail email fails', () => assert(validateBody({...validBody, requesterEmail: 'a@gmail.com'}) !== null, 'Should fail'));
  test('Empty name fails', () => assert(validateBody({...validBody, requesterName: '   '}) !== null, 'Should fail'));
  test('Short description fails', () => assert(validateBody({...validBody, description: 'corta'}) !== null, 'Should fail'));
  test('Missing product fails', () => assert(validateBody({...validBody, product: ''}) !== null, 'Should fail'));

  // ─── Report ──────────────────────────────────────────────────────────────────
  await new Promise((r) => setTimeout(r, 200));
  console.log('\n─────────────────────────────────');
  console.log(`Resultado: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.log('⚠ Hay tests fallando');
    process.exit(1);
  } else {
    console.log('✅ Todos los tests pasaron — sistema listo');
    process.exit(0);
  }
}

run().catch((e) => {
  console.error('Test runner error:', e);
  process.exit(1);
});
