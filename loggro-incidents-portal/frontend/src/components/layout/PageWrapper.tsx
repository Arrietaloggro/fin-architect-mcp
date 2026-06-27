import React from 'react';

interface PageWrapperProps {
  children: React.ReactNode;
  className?: string;
}

export function PageWrapper({ children, className = '' }: PageWrapperProps) {
  return (
    <main className={`max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in ${className}`}>
      {children}
    </main>
  );
}
