import React from 'react';
import { useLocation, Link, Navigate } from 'react-router-dom';
import { TicketResult } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { PageWrapper } from '../components/layout/PageWrapper';

const PRIORITY_COLORS: Record<string, 'red' | 'orange' | 'yellow' | 'green'> = {
  Crítica: 'red', Alta: 'orange', Media: 'yellow', Baja: 'green',
};

function formatDate(iso: string): { date: string; time: string } {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
    time: d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
  };
}

export function Confirmation() {
  const location = useLocation();
  const result = location.state as TicketResult | null;

  if (!result) return <Navigate to="/" replace />;

  const { date, time } = formatDate(result.createdAt);

  return (
    <PageWrapper className="flex justify-center">
      <div className="w-full max-w-lg animate-slide-up">
        {/* Success icon */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">¡Ticket creado exitosamente!</h1>
          <p className="text-gray-500 text-sm mt-2">
            Tu solicitud ha sido registrada y el equipo correspondiente la recibirá en breve.
          </p>
        </div>

        <Card padding="none" className="overflow-hidden">
          {/* Header */}
          <div className="bg-loggro-600 px-6 py-5 text-white">
            <div className="flex items-center justify-between">
              <span className="text-loggro-200 text-xs font-medium uppercase tracking-wider">Número de Ticket</span>
              {result.ticketUrl && (
                <a
                  href={result.ticketUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-loggro-200 hover:text-white flex items-center gap-1 transition-colors"
                >
                  Ver en Intercom
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              )}
            </div>
            <p className="text-3xl font-bold mt-1 font-mono">#{result.ticketId}</p>
          </div>

          {/* Details */}
          <div className="divide-y divide-gray-100">
            {[
              { label: 'Fecha', value: date },
              { label: 'Hora', value: time },
              { label: 'Producto', value: result.product },
              { label: 'Prioridad', value: (
                <Badge color={PRIORITY_COLORS[result.priority] || 'gray'}>{result.priority}</Badge>
              )},
              { label: 'Solicitante', value: result.requesterName },
              result.companyName ? { label: 'Empresa', value: result.companyName } : null,
              { label: 'Estado', value: (
                <Badge color="green">Registrado en Intercom</Badge>
              )},
            ].filter(Boolean).map((row, i) => (
              <div key={i} className="flex items-center justify-between px-6 py-3.5">
                <span className="text-sm text-gray-500">{(row as { label: string }).label}</span>
                <span className="text-sm font-medium text-gray-900 text-right max-w-[60%]">
                  {(row as { value: React.ReactNode }).value}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* Info box */}
        <div className="mt-4 rounded-xl bg-blue-50 border border-blue-200 px-4 py-4 flex gap-3">
          <svg className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <p className="text-sm text-blue-700">
            El ticket fue asignado automáticamente al equipo correspondiente según las reglas configuradas en Intercom.
            Recibirás actualizaciones según el SLA de la prioridad seleccionada.
          </p>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <Link to="/" className="flex-1">
            <Button variant="secondary" className="w-full" size="lg">
              Registrar otra incidencia
            </Button>
          </Link>
          {result.ticketUrl && (
            <a href={result.ticketUrl} target="_blank" rel="noopener noreferrer" className="flex-1">
              <Button className="w-full" size="lg">
                Ver ticket en Intercom
              </Button>
            </a>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
