export interface DynamicField {
  id: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'number';
  label: string;
  required: boolean;
  options?: string[];
  placeholder?: string;
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

export interface PortalConfig {
  products: Product[];
  requestTypes: RequestType[];
  priorities: Priority[];
  teams: Team[];
}

export interface TicketFormData {
  requesterName: string;
  requesterEmail: string;
  companyName: string;
  companyNit: string;
  product: string;
  requestType: string;
  priority: string;
  operationalImpact: string;
  description: string;
  dynamicFields: Record<string, string>;
  attachments: File[];
}

export interface TicketResult {
  success: boolean;
  ticketId: string;
  ticketUrl?: string;
  historyId: number;
  createdAt: string;
  product: string;
  priority: string;
  requesterName: string;
  companyName?: string;
}

export interface HistoryRecord {
  id: number;
  created_at: string;
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
  response_time_ms?: number;
}
