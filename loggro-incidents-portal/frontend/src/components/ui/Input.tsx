import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
}

export function Input({ label, error, hint, leftIcon, className = '', id, ...props }: InputProps) {
  const inputId = id || label.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="text-sm font-medium text-gray-700">
        {label}
        {props.required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
            {leftIcon}
          </div>
        )}
        <input
          id={inputId}
          {...props}
          className={`
            w-full rounded-lg border text-sm text-gray-900 placeholder-gray-400
            transition-colors duration-150 focus:outline-none focus:ring-2
            ${leftIcon ? 'pl-10' : 'pl-3'} pr-3 py-2.5
            ${error
              ? 'border-red-300 focus:border-red-400 focus:ring-red-200 bg-red-50'
              : 'border-gray-300 focus:border-loggro-400 focus:ring-loggro-100 bg-white'
            }
            disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
            ${className}
          `}
        />
      </div>
      {error && <p className="text-xs text-red-600 flex items-center gap-1"><span>⚠</span> {error}</p>}
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
    </div>
  );
}
