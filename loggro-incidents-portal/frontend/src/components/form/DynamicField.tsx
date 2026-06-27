import React from 'react';
import { DynamicField as DynamicFieldType } from '../../types';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Textarea } from '../ui/Textarea';

interface DynamicFieldProps {
  field: DynamicFieldType;
  value: string;
  onChange: (id: string, value: string) => void;
  error?: string;
}

export function DynamicField({ field, value, onChange, error }: DynamicFieldProps) {
  const handleChange = (val: string) => onChange(field.id, val);

  if (field.type === 'select') {
    return (
      <Select
        label={field.label}
        required={field.required}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        options={(field.options || []).map((o) => ({ value: o, label: o }))}
        placeholder="Selecciona una opción"
        error={error}
      />
    );
  }

  if (field.type === 'textarea') {
    return (
      <Textarea
        label={field.label}
        required={field.required}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={field.placeholder}
        error={error}
      />
    );
  }

  return (
    <Input
      label={field.label}
      required={field.required}
      value={value}
      onChange={(e) => handleChange(e.target.value)}
      placeholder={field.placeholder}
      type={field.type === 'number' ? 'number' : 'text'}
      error={error}
    />
  );
}
