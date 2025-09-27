import apiClient from './api';

const brokerService = {
  /**
   * Fetches a list of all available brokers from the backend.
   * @returns {Promise<Array>} A promise that resolves to an array of broker objects.
   */
  getBrokers() {
    return apiClient.get('/brokers');
  },
};

export default brokerService;