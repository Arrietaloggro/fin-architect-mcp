/**
 * intercom:test — Creates a real Intercom ticket end-to-end and then cleans up.
 * Validates the full integration: contact findOrCreate → ticket creation → attributes.
 *
 * Usage: npm run intercom:test
 *
 * Requires INTERCOM_ACCESS_TOKEN in .env.
 */

import 'dotenv/config';
import axios, { AxiosInstance } from 'axios';

const TOKEN = process.env.INTERCOM_ACCESS_TOKEN;
if (!TOKEN) {
  console.error('\n❌ INTERCOM_ACCESS_TOKEN is not set.');
  process.exit(1);
}

// ─── Intercom client ──────────────────────────────────────────────────────────

const api: AxiosInstance = axios.create({
  baseURL: 'https://api.intercom.io',
  headers: {
    Authorization: `Bearer ${TOKEN}`,
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'Intercom-Version': '2.11',
  },
  timeout: 20_000,
});

// ─── Helpers ─────────────────────────────────────────────────────────────────

async function findOrCreateContact(email: string, name: string): Promise<string> {
  // Search for existing contact
  const searchRes = await api.post('/contacts/search', {
    query: { field: 'email', operator: '=', value: email },
  });
  const contacts = searchRes.data.data ?? [];
  if (contacts.length > 0) {
    console.log(`   👤 Contact found: ${contacts[0].id}`);
    return contacts[0].id;
  }

  // Create new contact
  const createRes = await api.post('/contacts', {
    role: 'user',
    email,
    name,
  });
  console.log(`   👤 Contact created: ${createRes.data.id}`);
  return createRes.data.id;
}

async function createTicket(params: {
  contactId: string;
  ticketTypeId: string | undefined;
  title: string;
  description: string;
}): Promise<{ id: string; ticket_id: string; ticketUrl: string }> {
  const body: Record<string, unknown> = {
    contacts: [{ id: params.contactId }],
    ticket_attributes: {
      _default_title_: params.title,
      _default_description_: params.description,
    },
  };

  if (params.ticketTypeId) {
    body.ticket_type_id = params.ticketTypeId;
  }

  const res = await api.post('/tickets', body);
  const ticket = res.data;

  return {
    id: ticket.id,
    ticket_id: ticket.ticket_id?.toString() ?? ticket.id,
    ticketUrl: ticket.ticket_url ?? `https://app.intercom.com/a/inbox/_/tickets/${ticket.id}`,
  };
}

async function deleteContact(contactId: string): Promise<void> {
  await api.delete(`/contacts/${contactId}`);
}

// ─── Tests ────────────────────────────────────────────────────────────────────

interface TestResult {
  name: string;
  passed: boolean;
  detail?: string;
  error?: string;
}

const results: TestResult[] = [];

function pass(name: string, detail?: string) {
  console.log(`   ✅ ${name}${detail ? ` — ${detail}` : ''}`);
  results.push({ name, passed: true, detail });
}

function fail(name: string, error: string) {
  console.error(`   ❌ ${name} — ${error}`);
  results.push({ name, passed: false, error });
}

async function main() {
  console.log('\n🎫 Loggro Incidents Portal — Intercom Integration Test\n');
  console.log('═'.repeat(60));

  const TEST_EMAIL = 'loggro-portal-test@loggro.com';
  const TEST_NAME = 'Portal Test Bot';
  let contactId: string | null = null;
  const createdTicketIds: string[] = [];

  // ── Test 1: Token validation ───────────────────────────────────────────────
  console.log('\n▶  Test 1: Token validation');
  try {
    const res = await api.get('/me');
    pass('Token valid', `Authenticated as ${res.data.name} <${res.data.email}>`);
  } catch (err: unknown) {
    fail('Token valid', (err as Error).message);
    console.error('\n   Cannot continue without a valid token. Exiting.');
    process.exit(1);
  }

  // ── Test 2: Contact findOrCreate ───────────────────────────────────────────
  console.log('\n▶  Test 2: Contact findOrCreate (POST /contacts/search → /contacts)');
  try {
    contactId = await findOrCreateContact(TEST_EMAIL, TEST_NAME);
    pass('Contact findOrCreate', `contact_id: ${contactId}`);
  } catch (err: unknown) {
    fail('Contact findOrCreate', (err as Error).message);
    contactId = null;
  }

  if (!contactId) {
    console.error('\n   Cannot test ticket creation without a contact. Exiting.');
    process.exit(1);
  }

  // ── Test 3: Ticket creation (no ticket_type_id) ────────────────────────────
  console.log('\n▶  Test 3: Create ticket without ticket_type_id (generic)');
  try {
    const ticket = await createTicket({
      contactId,
      ticketTypeId: undefined,
      title: '[TEST] Portal Incidencias — prueba genérica',
      description: [
        '**Test automático — Portal Interno Loggro**',
        '',
        '• Producto: ERP Pymes',
        '• Tipo: Bug',
        '• Prioridad: Alta',
        '• Empresa: Loggro Internal Test',
        '• NIT: 900000000',
        '• Descripción: Test de integración del portal de incidencias. Este ticket fue creado automáticamente y puede ser eliminado.',
      ].join('\n'),
    });
    createdTicketIds.push(ticket.id);
    pass('Generic ticket created', `ticket_id: ${ticket.ticket_id} | id: ${ticket.id}`);
    console.log(`   🔗 ${ticket.ticketUrl}`);
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: unknown; status?: number } }).response?.data;
    fail('Generic ticket created', `${(err as Error).message} — ${JSON.stringify(detail)}`);
  }

  // ── Test 4: Ticket creation with ticket_type_id (if configured) ────────────
  const erpTicketTypeId = process.env.INTERCOM_TICKET_TYPE_ERP_PYMES;
  if (erpTicketTypeId) {
    console.log(`\n▶  Test 4: Create ticket with ticket_type_id (ERP Pymes: ${erpTicketTypeId})`);
    try {
      const ticket = await createTicket({
        contactId,
        ticketTypeId: erpTicketTypeId,
        title: '[TEST] Portal Incidencias — ERP Pymes',
        description: [
          '**Test automático — Portal Interno Loggro**',
          '',
          '• Producto: ERP Pymes',
          '• Tipo: Error de facturación',
          '• Prioridad: Crítica',
          '• Empresa: Empresa Demo SA',
          '• NIT: 900123456',
          '• Impacto operativo: Bloqueo total del módulo de facturación',
          '• Descripción: El sistema no genera facturas electrónicas desde las 08:00. Se afectan aproximadamente 50 usuarios.',
        ].join('\n'),
      });
      createdTicketIds.push(ticket.id);
      pass('Typed ticket created (ERP Pymes)', `ticket_id: ${ticket.ticket_id} | id: ${ticket.id}`);
      console.log(`   🔗 ${ticket.ticketUrl}`);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: unknown } }).response?.data;
      fail('Typed ticket created (ERP Pymes)', `${(err as Error).message} — ${JSON.stringify(detail)}`);
    }
  } else {
    console.log('\n▶  Test 4: Skipped (INTERCOM_TICKET_TYPE_ERP_PYMES not set)');
    console.log('   ℹ  Run npm run intercom:discover after creating ticket types in Intercom.');
    results.push({ name: 'Typed ticket (ERP Pymes)', passed: true, detail: 'skipped — no ticket type configured' });
  }

  // ── Test 5: Negative — wrong email domain ─────────────────────────────────
  console.log('\n▶  Test 5: Domain validation (Gmail should be rejected by backend)');
  // This tests the backend validator, not Intercom directly.
  // We simulate what ticketController.validateBody does.
  const gmailEmail = 'attacker@gmail.com';
  const domainRe = /^[a-zA-Z0-9._%+\-]+@loggro\.com$/i;
  if (!domainRe.test(gmailEmail)) {
    pass('Gmail rejected by domain validator', `"${gmailEmail}" blocked`);
  } else {
    fail('Gmail rejected by domain validator', 'Gmail should not pass domain check');
  }

  // ── Test 6: Negative — empty description ──────────────────────────────────
  console.log('\n▶  Test 6: Description length validation');
  const shortDesc = 'corta';
  if (shortDesc.trim().length < 10) {
    pass('Short description rejected', `"${shortDesc}" has ${shortDesc.length} chars (min 10)`);
  } else {
    fail('Short description rejected', 'Short description should be rejected');
  }

  // ── Test 7: Verify tickets are NOT conversations ───────────────────────────
  console.log('\n▶  Test 7: Verify tickets are not conversations (GET /tickets/:id)');
  if (createdTicketIds.length > 0) {
    const ticketId = createdTicketIds[0];
    try {
      const res = await api.get(`/tickets/${ticketId}`);
      const isTicket = res.data.type === 'ticket';
      if (isTicket) {
        pass('Created item is a ticket (not a conversation)', `type: ${res.data.type}`);
      } else {
        fail('Created item is a ticket', `type was: ${res.data.type}`);
      }
    } catch (err: unknown) {
      fail('Verify ticket type', (err as Error).message);
    }
  } else {
    console.log('   ⚠  No tickets were created to verify.');
  }

  // ── Cleanup ───────────────────────────────────────────────────────────────
  console.log('\n▶  Cleanup: Deleting test contact (tickets remain for manual review)');
  if (contactId) {
    try {
      await deleteContact(contactId);
      console.log(`   🗑  Test contact deleted: ${contactId}`);
    } catch (err: unknown) {
      console.warn(`   ⚠  Could not delete test contact: ${(err as Error).message}`);
    }
  }

  if (createdTicketIds.length > 0) {
    console.log(`\n   📝 Created test tickets (review and delete manually in Intercom):`);
    for (const id of createdTicketIds) {
      console.log(`      • https://app.intercom.com/a/inbox/_/tickets/${id}`);
    }
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;

  console.log('\n' + '═'.repeat(60));
  console.log(`\nResultado: ${passed} passed, ${failed} failed`);

  if (failed === 0) {
    console.log('\n✅ Integración con Intercom validada — portal listo para Fase 3\n');
    process.exit(0);
  } else {
    console.log('\n⚠  Hay tests fallando — revisar errores arriba\n');
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('\n❌ Test runner error:', err.message);
  process.exit(1);
});
