import React from 'react';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-loggro-600 rounded-lg flex items-center justify-center shadow-sm">
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-white" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <span className="font-semibold text-gray-900 text-sm">Portal de Incidencias</span>
            <span className="ml-2 text-xs text-loggro-600 font-medium bg-loggro-50 px-2 py-0.5 rounded-full">Interno</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 hidden sm:block">Solo para equipos @loggro.com</span>
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-soft" title="Sistema operativo" />
        </div>
      </div>
    </header>
  );
}
