import React from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
  hint?: string;
}

export function Textarea({ label, error, hint, className = '', id, ...props }: TextareaProps) {
  const textareaId = id || label.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={textareaId} className="text-sm font-medium text-gray-700">
        {label}
        {props.required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <textarea
        id={textareaId}
        {...props}
        className={`
          w-full rounded-lg border text-sm text-gray-900 placeholder-gray-400
          px-3 py-2.5 resize-y min-h-[100px]
          transition-colors duration-150 focus:outline-none focus:ring-2
          ${error
            ? 'border-red-300 focus:border-red-400 focus:ring-red-200 bg-red-50'
            : 'border-gray-300 focus:border-loggro-400 focus:ring-loggro-100 bg-white'
          }
          disabled:bg-gray-50 disabled:cursor-not-allowed
          ${className}
        `}
      />
      {error && <p className="text-xs text-red-600 flex items-center gap-1"><span>⚠</span> {error}</p>}
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
    </div>
  );
}
