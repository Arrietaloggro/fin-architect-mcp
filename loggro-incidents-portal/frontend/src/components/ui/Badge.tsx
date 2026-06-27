import React from 'react';

type Color = 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple' | 'gray';

interface BadgeProps {
  color?: Color;
  children: React.ReactNode;
  size?: 'sm' | 'md';
}

const colorClasses: Record<Color, string> = {
  red:    'bg-red-100 text-red-700 border-red-200',
  orange: 'bg-orange-100 text-orange-700 border-orange-200',
  yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  green:  'bg-emerald-100 text-emerald-700 border-emerald-200',
  blue:   'bg-blue-100 text-blue-700 border-blue-200',
  purple: 'bg-purple-100 text-purple-700 border-purple-200',
  gray:   'bg-gray-100 text-gray-700 border-gray-200',
};

export function Badge({ color = 'gray', children, size = 'md' }: BadgeProps) {
  return (
    <span className={`
      inline-flex items-center border font-medium rounded-full
      ${size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'}
      ${colorClasses[color]}
    `}>
      {children}
    </span>
  );
}
