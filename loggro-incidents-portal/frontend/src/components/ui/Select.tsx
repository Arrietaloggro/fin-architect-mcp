import React from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: SelectOption[];
  error?: string;
  hint?: string;
  placeholder?: string;
}

export function Select({ label, options, error, hint, placeholder, className = '', id, ...props }: SelectProps) {
  const selectId = id || label.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={selectId} className="text-sm font-medium text-gray-700">
        {label}
        {props.required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <div className="relative">
        <select
          id={selectId}
          {...props}
          className={`
            w-full rounded-lg border text-sm text-gray-900 pl-3 pr-8 py-2.5
            appearance-none bg-white transition-colors duration-150
            focus:outline-none focus:ring-2
            ${error
              ? 'border-red-300 focus:border-red-400 focus:ring-red-200 bg-red-50'
              : 'border-gray-300 focus:border-loggro-400 focus:ring-loggro-100'
            }
            disabled:bg-gray-50 disabled:cursor-not-allowed
            ${className}
          `}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400">
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </div>
      </div>
      {error && <p className="text-xs text-red-600 flex items-center gap-1"><span>⚠</span> {error}</p>}
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
    </div>
  );
}
