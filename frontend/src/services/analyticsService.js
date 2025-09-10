// =============================================================================
// FILE: src/services/analyticsService.js
// DESCRIZIONE: Servizio per recuperare i dati di analytics dal backend.
// =============================================================================

import apiClient from './api';

/**
 * Simula il recupero dei dati per il grafico "Daily Net Cumulative P&L".
 * In una implementazione reale, questa funzione farebbe una chiamata al backend
 * con apiClient.get('/api/analytics/daily-net-cumulative-pl').
 *
 * @returns {Promise<Object>} Una promessa che risolve con i dati del grafico.
 */
export const fetchDailyNetCumulativePL = () => {
  console.log('Fetching mock data for Daily Net Cumulative P&L...');

  // Dati di esempio che simulano una risposta dal backend
  const mockData = {
    labels: ['05/01', '05/02', '05/03', '05/04', '05/05', '05/06', '05/07', '05/08'],
    data: [15200, 15350, 15300, 15500, 15650, 15800, 15750, 16050],
  };

  // Simulo un ritardo di rete di 1.5 secondi
  return new Promise(resolve => {
    setTimeout(() => {
      console.log('Mock data fetched.');
      resolve(mockData);
    }, 1500);
  });
};

// Qui potrebbero essere aggiunte altre funzioni per altri grafici...
// export const fetchWinLossRatio = () => { ... };
