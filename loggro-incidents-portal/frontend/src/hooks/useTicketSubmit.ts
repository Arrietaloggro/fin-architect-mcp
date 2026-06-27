import { useState } from 'react';
import { TicketFormData, TicketResult } from '../types';
import { submitTicket } from '../services/api';

export function useTicketSubmit() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (formData: TicketFormData): Promise<TicketResult | null> => {
    setSubmitting(true);
    setError(null);
    try {
      const result = await submitTicket(formData);
      return result;
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ||
        'Error al enviar el ticket. Por favor intenta nuevamente.';
      setError(msg);
      return null;
    } finally {
      setSubmitting(false);
    }
  };

  return { submit, submitting, error, clearError: () => setError(null) };
}
