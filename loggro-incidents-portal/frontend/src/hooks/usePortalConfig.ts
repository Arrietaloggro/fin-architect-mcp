import { useState, useEffect } from 'react';
import { PortalConfig } from '../types';
import { fetchPortalConfig } from '../services/api';

export function usePortalConfig() {
  const [config, setConfig] = useState<PortalConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPortalConfig()
      .then(setConfig)
      .catch(() => setError('No se pudo cargar la configuración del portal. Recarga la página.'))
      .finally(() => setLoading(false));
  }, []);

  return { config, loading, error };
}
