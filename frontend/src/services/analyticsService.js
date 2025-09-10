// =============================================================================
// FILE: src/services/analyticsService.js
// DESCRIZIONE: Servizio per recuperare i dati di analytics dal backend.
// =============================================================================

import apiClient from './api';

/**
 * Recupera i dati per il grafico della curva di equity (Daily Net Cumulative P&L)
 * dal backend, con la possibilità di applicare filtri.
 *
 * @param {Object} [filters={}] - Un oggetto contenente i filtri da applicare.
 * @param {Date} [filters.startDate] - La data di inizio del periodo.
 * @param {Date} [filters.endDate] - La data di fine del periodo.
 * @param {string} [filters.strategy] - La strategia da filtrare.
 * @returns {Promise<Object>} Una promessa che risolve con i dati del grafico.
 */
export const fetchDailyNetCumulativePL = async (filters = {}) => {
  const { startDate, endDate, strategy } = filters;

  // Costruiamo dinamicamente i parametri per la richiesta
  const params = new URLSearchParams();
  if (startDate) {
    params.append('start_date', startDate.toISOString().split('T')[0]); // Formato YYYY-MM-DD
  }
  if (endDate) {
    params.append('end_date', endDate.toISOString().split('T')[0]); // Formato YYYY-MM-DD
  }
  if (strategy && strategy !== 'all') {
    params.append('strategy', strategy);
  }

  try {
    const endpoint = `/api/v1/trades/equity-curve?${params.toString()}`;
    console.log(`Fetching data for Equity Curve from ${endpoint}`);

    const response = await apiClient.get('/api/v1/trades/equity-curve', { params });

    console.log('Equity Curve data fetched successfully.');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch equity curve data:', error);
    // In caso di errore, restituiamo un oggetto vuoto per evitare che il
    // componente del grafico vada in errore. Il placeholder verrà mostrato.
    return { labels: [], data: [] };
  }
};

// Qui potrebbero essere aggiunte altre funzioni per altri grafici...
// export const fetchWinLossRatio = () => { ... };
