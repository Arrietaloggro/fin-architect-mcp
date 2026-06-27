import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePortalConfig } from '../hooks/usePortalConfig';
import { useTicketSubmit } from '../hooks/useTicketSubmit';
import { TicketFormData } from '../types';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Textarea } from '../components/ui/Textarea';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { FileUpload } from '../components/ui/FileUpload';
import { ProductSelector } from '../components/form/ProductSelector';
import { DynamicField } from '../components/form/DynamicField';
import { FormSection } from '../components/form/FormSection';
import { PageWrapper } from '../components/layout/PageWrapper';

type FormErrors = Partial<Record<string, string>>;

const INITIAL_FORM: TicketFormData = {
  requesterName: '',
  requesterEmail: '',
  companyName: '',
  companyNit: '',
  product: '',
  requestType: '',
  priority: '',
  operationalImpact: '',
  description: '',
  dynamicFields: {},
  attachments: [],
};

const PRIORITY_COLORS: Record<string, 'red' | 'orange' | 'yellow' | 'green'> = {
  critical: 'red', high: 'orange', medium: 'yellow', low: 'green',
};

const OPERATIONAL_IMPACT_OPTIONS = [
  { value: 'no', label: 'No, solo afecta funcionalidades secundarias' },
  { value: 'partial', label: 'Sí, parcialmente — hay workaround disponible' },
  { value: 'critical', label: 'Sí, crítico — operaciones detenidas' },
];

function validateEmail(email: string): boolean {
  return /^[a-zA-Z0-9._%+\-]+@loggro\.com$/i.test(email);
}

function validate(form: TicketFormData): FormErrors {
  const errors: FormErrors = {};
  if (!form.requesterName.trim()) errors.requesterName = 'El nombre es requerido.';
  if (!form.requesterEmail.trim()) errors.requesterEmail = 'El correo es requerido.';
  else if (!validateEmail(form.requesterEmail)) errors.requesterEmail = 'Debes usar tu correo corporativo @loggro.com.';
  if (!form.companyName.trim()) errors.companyName = 'El nombre de la empresa cliente es requerido.';
  if (!form.product) errors.product = 'Selecciona el producto afectado.';
  if (!form.requestType) errors.requestType = 'Selecciona el tipo de solicitud.';
  if (!form.priority) errors.priority = 'Selecciona la prioridad.';
  if (!form.operationalImpact) errors.operationalImpact = 'Indica si hay impacto operativo.';
  if (!form.description.trim()) errors.description = 'La descripción es requerida.';
  else if (form.description.trim().length < 20) errors.description = 'La descripción debe tener al menos 20 caracteres.';
  return errors;
}

export function IncidentForm() {
  const { config, loading: configLoading, error: configError } = usePortalConfig();
  const { submit, submitting, error: submitError, clearError } = useTicketSubmit();
  const navigate = useNavigate();

  const [form, setForm] = useState<TicketFormData>(INITIAL_FORM);
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Set<string>>(new Set());

  const set = (field: keyof TicketFormData, value: unknown) => {
    setForm((prev) => {
      const updated = { ...prev, [field]: value };
      if (field === 'product') {
        updated.dynamicFields = {};
      }
      return updated;
    });
    clearError();
  };

  const setDynamic = (id: string, value: string) => {
    setForm((prev) => ({ ...prev, dynamicFields: { ...prev.dynamicFields, [id]: value } }));
  };

  const touch = (field: string) => setTouched((prev) => new Set(prev).add(field));

  const currentProduct = config?.products.find((p) => p.id === form.product);
  const currentPriority = config?.priorities.find((p) => p.id === form.priority);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validation = validate(form);
    setErrors(validation);
    setTouched(new Set(Object.keys(validation)));

    if (Object.keys(validation).length > 0) {
      const firstErrorKey = Object.keys(validation)[0];
      document.getElementById(firstErrorKey)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    const result = await submit(form);
    if (result) {
      navigate('/confirmation', { state: result });
    }
  };

  if (configLoading) {
    return (
      <PageWrapper>
        <div className="flex justify-center py-24">
          <Spinner size="lg" text="Cargando configuración del portal..." />
        </div>
      </PageWrapper>
    );
  }

  if (configError || !config) {
    return (
      <PageWrapper>
        <Card className="text-center py-12">
          <p className="text-red-600 font-medium">{configError}</p>
          <Button variant="secondary" className="mt-4" onClick={() => window.location.reload()}>
            Reintentar
          </Button>
        </Card>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      {/* Hero section */}
      <div className="mb-8 text-center sm:text-left">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Registrar incidencia o solicitud</h1>
        <p className="mt-1.5 text-gray-500 text-sm max-w-xl">
          Completa el formulario para crear un ticket de soporte directamente en nuestro sistema.
          Recibirás una confirmación inmediata con el número de ticket asignado.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
        {/* Solicitante */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-loggro-100 text-loggro-700 text-xs font-bold flex items-center justify-center">1</span>
              Información del solicitante
            </h2>
          </CardHeader>
          <FormSection title="Datos de contacto" description="Información del miembro del equipo Loggro que registra la solicitud">
            <Input
              id="requesterName"
              label="Nombre completo"
              required
              value={form.requesterName}
              onChange={(e) => set('requesterName', e.target.value)}
              onBlur={() => touch('requesterName')}
              error={touched.has('requesterName') ? errors.requesterName : undefined}
              placeholder="Tu nombre completo"
              autoComplete="name"
            />
            <Input
              id="requesterEmail"
              label="Correo corporativo"
              required
              type="email"
              value={form.requesterEmail}
              onChange={(e) => set('requesterEmail', e.target.value)}
              onBlur={() => touch('requesterEmail')}
              error={touched.has('requesterEmail') ? errors.requesterEmail : undefined}
              placeholder="nombre@loggro.com"
              autoComplete="email"
              hint="Solo correos @loggro.com son aceptados"
            />
          </FormSection>
        </Card>

        {/* Empresa cliente */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-loggro-100 text-loggro-700 text-xs font-bold flex items-center justify-center">2</span>
              Empresa cliente afectada
            </h2>
          </CardHeader>
          <FormSection title="Datos del cliente" description="Empresa que reporta el problema o para quien va la solicitud">
            <Input
              id="companyName"
              label="Nombre de la empresa"
              required
              value={form.companyName}
              onChange={(e) => set('companyName', e.target.value)}
              onBlur={() => touch('companyName')}
              error={touched.has('companyName') ? errors.companyName : undefined}
              placeholder="Ej: Empresa S.A.S."
            />
            <Input
              id="companyNit"
              label="NIT"
              value={form.companyNit}
              onChange={(e) => set('companyNit', e.target.value)}
              placeholder="Ej: 900.123.456-7"
              hint="Opcional"
            />
          </FormSection>
        </Card>

        {/* Producto */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-loggro-100 text-loggro-700 text-xs font-bold flex items-center justify-center">3</span>
              Producto y tipo de solicitud
            </h2>
          </CardHeader>
          <div className="grid grid-cols-1 gap-6">
            <ProductSelector
              products={config.products}
              value={form.product}
              onChange={(id) => set('product', id)}
              error={touched.has('product') ? errors.product : undefined}
            />

            {/* Dynamic fields per product */}
            {currentProduct && currentProduct.dynamicFields.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-slide-up">
                {currentProduct.dynamicFields.map((field) => (
                  <DynamicField
                    key={field.id}
                    field={field}
                    value={form.dynamicFields[field.id] || ''}
                    onChange={setDynamic}
                  />
                ))}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Select
                id="requestType"
                label="Tipo de solicitud"
                required
                value={form.requestType}
                onChange={(e) => set('requestType', e.target.value)}
                onBlur={() => touch('requestType')}
                options={config.requestTypes.map((r) => ({ value: r.id, label: r.name }))}
                placeholder="Selecciona el tipo"
                error={touched.has('requestType') ? errors.requestType : undefined}
              />

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">
                  Prioridad <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {config.priorities.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => set('priority', p.id)}
                      className={`
                        flex flex-col gap-0.5 p-2.5 rounded-lg border-2 text-left transition-all duration-150
                        ${form.priority === p.id
                          ? 'border-loggro-500 bg-loggro-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      <Badge color={PRIORITY_COLORS[p.id] || 'gray'} size="sm">{p.name}</Badge>
                      <span className="text-xs text-gray-500 leading-tight">SLA {p.slaHours}h</span>
                    </button>
                  ))}
                </div>
                {touched.has('priority') && errors.priority && (
                  <p className="text-xs text-red-600">⚠ {errors.priority}</p>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Descripción */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-loggro-100 text-loggro-700 text-xs font-bold flex items-center justify-center">4</span>
              Descripción del problema
            </h2>
          </CardHeader>
          <div className="flex flex-col gap-4">
            <Select
              id="operationalImpact"
              label="¿Hay impacto operativo en el cliente?"
              required
              value={form.operationalImpact}
              onChange={(e) => set('operationalImpact', e.target.value)}
              onBlur={() => touch('operationalImpact')}
              options={OPERATIONAL_IMPACT_OPTIONS}
              placeholder="Selecciona el nivel de impacto"
              error={touched.has('operationalImpact') ? errors.operationalImpact : undefined}
            />

            <Textarea
              id="description"
              label="Descripción detallada"
              required
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
              onBlur={() => touch('description')}
              rows={5}
              placeholder="Describe el problema o solicitud con el mayor detalle posible. Incluye: qué ocurre, cuándo empezó, pasos para reproducirlo, mensajes de error, impacto en el negocio..."
              error={touched.has('description') ? errors.description : undefined}
            />

            <FileUpload
              onChange={(files) => set('attachments', files)}
              maxFiles={5}
              maxSizeMb={10}
            />
          </div>
        </Card>

        {/* Preview & submit */}
        {form.product && form.requestType && form.priority && (
          <Card className="bg-loggro-50 border-loggro-200 animate-slide-up">
            <p className="text-sm font-medium text-loggro-800 mb-2">Resumen del ticket a crear:</p>
            <div className="flex flex-wrap gap-2">
              {currentProduct && <Badge color="blue">{currentProduct.name}</Badge>}
              <Badge color="gray">{config.requestTypes.find(r => r.id === form.requestType)?.name}</Badge>
              {currentPriority && <Badge color={PRIORITY_COLORS[currentPriority.id] || 'gray'}>{currentPriority.name}</Badge>}
              {form.companyName && <Badge color="gray">{form.companyName}</Badge>}
            </div>
          </Card>
        )}

        {submitError && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-start gap-3">
            <svg className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-red-700">{submitError}</p>
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3 justify-end pb-4">
          <Button
            type="button"
            variant="secondary"
            size="lg"
            onClick={() => { setForm(INITIAL_FORM); setErrors({}); setTouched(new Set()); }}
          >
            Limpiar formulario
          </Button>
          <Button type="submit" size="lg" loading={submitting}>
            {submitting ? 'Creando ticket...' : 'Crear ticket de soporte'}
          </Button>
        </div>
      </form>
    </PageWrapper>
  );
}
