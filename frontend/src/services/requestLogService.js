import apiClient from './api';

const requestLogService = {
  /**
   * Recupera i log delle richieste dal backend.
   * @param {object} params - Parametri per la query (limit, offset, sort_by, sort_order, status_code_filter).
   * @returns {Promise<object>} Una promessa che risolve con i dati della risposta.
   */
  getRequestLogs(params) {
    return apiClient.get('/request-logs', { params });
  },

  /**
   * Cancella tutti i log delle richieste dal backend.
   * @returns {Promise<object>} Una promessa che risolve con i dati della risposta.
   */
  clearRequestLogs() {
    return apiClient.delete('/request-logs');
  },
};

export default requestLogService;