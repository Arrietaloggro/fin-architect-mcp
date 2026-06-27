import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg' | 'none';
}

const paddings = { none: '', sm: 'p-4', md: 'p-6', lg: 'p-8' };

export function Card({ children, className = '', padding = 'md' }: CardProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${paddings[padding]} ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`border-b border-gray-100 pb-4 mb-6 ${className}`}>
      {children}
    </div>
  );
}
