import React from 'react';

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
}

export function FormSection({ title, description, children, icon }: FormSectionProps) {
  return (
    <section className="animate-slide-up">
      <div className="flex items-start gap-3 mb-4">
        {icon && (
          <div className="w-8 h-8 rounded-lg bg-loggro-50 flex items-center justify-center text-loggro-600 flex-shrink-0 mt-0.5">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          {description && <p className="text-xs text-gray-500 mt-0.5">{description}</p>}
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {children}
      </div>
    </section>
  );
}
