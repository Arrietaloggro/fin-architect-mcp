import React from 'react';
import { Product } from '../../types';

interface ProductSelectorProps {
  products: Product[];
  value: string;
  onChange: (productId: string) => void;
  error?: string;
}

export function ProductSelector({ products, value, onChange, error }: ProductSelectorProps) {
  return (
    <div className="flex flex-col gap-2 sm:col-span-2">
      <span className="text-sm font-medium text-gray-700">
        Producto / Sistema afectado <span className="text-red-500">*</span>
      </span>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {products.map((product) => {
          const isSelected = value === product.id;
          return (
            <button
              key={product.id}
              type="button"
              onClick={() => onChange(product.id)}
              className={`
                relative flex flex-col items-start gap-1.5 p-3 rounded-xl border-2 text-left
                transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-loggro-400
                ${isSelected
                  ? 'border-loggro-500 bg-loggro-50 shadow-sm'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              <span className="text-xl leading-none">{product.icon}</span>
              <div>
                <p className={`text-xs font-semibold ${isSelected ? 'text-loggro-700' : 'text-gray-800'}`}>
                  {product.name}
                </p>
                <p className="text-xs text-gray-500 leading-tight mt-0.5 hidden sm:block">
                  {product.description}
                </p>
              </div>
              {isSelected && (
                <div className="absolute top-2 right-2 w-4 h-4 rounded-full bg-loggro-600 flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>
      {error && <p className="text-xs text-red-600 flex items-center gap-1">⚠ {error}</p>}
    </div>
  );
}
