import { useEffect, useState } from 'react';

const dataUrl = import.meta.env.BASE_URL + 'data/';

export function useDashboardData(file = 'overview.json') {
  const [state, setState] = useState({ phase: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch(dataUrl + file, { signal: controller.signal, cache: 'no-cache' });
        if (!response.ok) throw new Error('Dataset non disponibile');
        const data = await response.json();
        if (file === 'overview.json' && (data?.schemaVersion !== 1 || !Array.isArray(data.forecast) || !Array.isArray(data.budgetScenario))) {
          throw new Error('Versione dei dati non supportata');
        }
        if (!controller.signal.aborted) setState({ phase: 'ready', data });
      } catch {
        if (!controller.signal.aborted) setState({ phase: 'error' });
      }
    }
    load();
    return () => controller.abort();
  }, [attempt, file]);
  return { ...state, retry: () => { setState({ phase: 'loading' }); setAttempt((n) => n + 1); } };
}

