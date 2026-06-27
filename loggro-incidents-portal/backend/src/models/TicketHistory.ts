import { getDb } from '../database/connection';

export interface TicketHistoryRecord {
  id?: number;
  created_at?: string;
  requester_name: string;
  requester_email: string;
  company_name?: string;
  company_nit?: string;
  product: string;
  request_type: string;
  priority: string;
  operational_impact?: string;
  description: string;
  intercom_ticket_id?: string;
  intercom_ticket_url?: string;
  status: 'pending' | 'success' | 'error';
  error_message?: string;
  ip_address?: string;
  user_agent?: string;
  response_time_ms?: number;
}

export interface HistoryFilters {
  page?: number;
  limit?: number;
  product?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  email?: string;
}

export class TicketHistoryModel {
  static create(record: Omit<TicketHistoryRecord, 'id' | 'created_at'>): number {
    const db = getDb();
    const stmt = db.prepare(`
      INSERT INTO ticket_history
        (requester_name, requester_email, company_name, company_nit, product, request_type,
         priority, operational_impact, description, intercom_ticket_id, intercom_ticket_url,
         status, error_message, ip_address, user_agent, response_time_ms)
      VALUES
        (@requester_name, @requester_email, @company_name, @company_nit, @product, @request_type,
         @priority, @operational_impact, @description, @intercom_ticket_id, @intercom_ticket_url,
         @status, @error_message, @ip_address, @user_agent, @response_time_ms)
    `);
    const result = stmt.run(record);
    return result.lastInsertRowid as number;
  }

  static updateStatus(
    id: number,
    status: 'success' | 'error',
    intercomTicketId?: string,
    intercomTicketUrl?: string,
    errorMessage?: string,
    responseTimeMs?: number
  ): void {
    const db = getDb();
    db.prepare(`
      UPDATE ticket_history
      SET status = ?, intercom_ticket_id = ?, intercom_ticket_url = ?,
          error_message = ?, response_time_ms = ?
      WHERE id = ?
    `).run(status, intercomTicketId ?? null, intercomTicketUrl ?? null, errorMessage ?? null, responseTimeMs ?? null, id);
  }

  static findAll(filters: HistoryFilters = {}): { records: TicketHistoryRecord[]; total: number } {
    const db = getDb();
    const page = filters.page ?? 1;
    const limit = filters.limit ?? 20;
    const offset = (page - 1) * limit;

    const conditions: string[] = [];
    const params: unknown[] = [];

    if (filters.product) { conditions.push('product = ?'); params.push(filters.product); }
    if (filters.status)  { conditions.push('status = ?');  params.push(filters.status);  }
    if (filters.email)   { conditions.push('requester_email LIKE ?'); params.push(`%${filters.email}%`); }
    if (filters.startDate) { conditions.push('created_at >= ?'); params.push(filters.startDate); }
    if (filters.endDate)   { conditions.push('created_at <= ?'); params.push(filters.endDate); }

    const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

    const total = (db.prepare(`SELECT COUNT(*) as count FROM ticket_history ${where}`).get(...params) as { count: number }).count;
    const records = db.prepare(
      `SELECT * FROM ticket_history ${where} ORDER BY created_at DESC LIMIT ? OFFSET ?`
    ).all(...params, limit, offset) as TicketHistoryRecord[];

    return { records, total };
  }

  static findById(id: number): TicketHistoryRecord | null {
    const db = getDb();
    return (db.prepare('SELECT * FROM ticket_history WHERE id = ?').get(id) as TicketHistoryRecord) ?? null;
  }

  static getStats(): Record<string, unknown> {
    const db = getDb();
    const total = (db.prepare('SELECT COUNT(*) as count FROM ticket_history').get() as { count: number }).count;
    const byStatus = db.prepare("SELECT status, COUNT(*) as count FROM ticket_history GROUP BY status").all();
    const byProduct = db.prepare("SELECT product, COUNT(*) as count FROM ticket_history GROUP BY product ORDER BY count DESC").all();
    const byPriority = db.prepare("SELECT priority, COUNT(*) as count FROM ticket_history GROUP BY priority").all();
    const today = db.prepare("SELECT COUNT(*) as count FROM ticket_history WHERE date(created_at) = date('now')").get() as { count: number };
    return { total, byStatus, byProduct, byPriority, today: today.count };
  }
}
