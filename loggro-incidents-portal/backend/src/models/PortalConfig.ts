import { getDb } from '../database/connection';

export interface PortalConfigData {
  products: Product[];
  requestTypes: RequestType[];
  priorities: Priority[];
  teams: Team[];
}

export interface Product {
  id: string;
  name: string;
  icon: string;
  color: string;
  active: boolean;
  description: string;
  intercomTicketTypeId: string;
  dynamicFields: DynamicField[];
}

export interface DynamicField {
  id: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'number';
  label: string;
  required: boolean;
  options?: string[];
  placeholder?: string;
}

export interface RequestType {
  id: string;
  name: string;
  active: boolean;
}

export interface Priority {
  id: string;
  name: string;
  color: string;
  slaHours: number;
  description: string;
}

export interface Team {
  id: string;
  name: string;
}

export class PortalConfigModel {
  static get(): PortalConfigData {
    const db = getDb();
    const row = db.prepare("SELECT config_value FROM portal_config WHERE config_key = 'main'").get() as
      | { config_value: string }
      | undefined;
    if (!row) throw new Error('Portal config not found in database');
    return JSON.parse(row.config_value) as PortalConfigData;
  }

  static set(data: PortalConfigData): void {
    const db = getDb();
    db.prepare(
      "INSERT INTO portal_config (config_key, config_value, updated_at) VALUES ('main', ?, CURRENT_TIMESTAMP) ON CONFLICT(config_key) DO UPDATE SET config_value = excluded.config_value, updated_at = CURRENT_TIMESTAMP"
    ).run(JSON.stringify(data));
  }

  static patch(partial: Partial<PortalConfigData>): PortalConfigData {
    const current = this.get();
    const updated = { ...current, ...partial };
    this.set(updated);
    return updated;
  }
}
