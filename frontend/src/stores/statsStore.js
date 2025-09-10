import { defineStore } from 'pinia';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';

export const useStatsStore = defineStore('stats', {
  state: () => ({
    vantageScore: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    /**
     * Il punteggio numerico del Vantage Score.
     * @returns {number} Il punteggio, o 0 se non disponibile.
     */
    vantageScoreValue: (state) => {
      return state.vantageScore?.vantage_score ?? 0;
    },

    /**
     * Formatta i dati del Vantage Score per il componente Radar di Chart.js.
     * @returns {object|null} L'oggetto dati per Chart.js o null se i dati non sono disponibili.
     */
    vantageChartData: (state) => {
      if (!state.vantageScore) {
        return null;
      }
      const scores = state.vantageScore;
      return {
        labels: ['Win %', 'Profit factor', 'Avg win/loss', 'Recovery factor', 'Max drawdown', 'Consistency'],
        datasets: [{
          label: 'Vantage Score',
          data: [
            scores.win_rate_score,
            scores.profit_factor_score,
            scores.avg_win_loss_score,
            scores.recovery_factor_score,
            scores.max_drawdown_score,
            scores.consistency_score,
          ],
          backgroundColor: 'rgba(var(--base-color-blue-600-rgb), 0.2)',
          borderColor: 'var(--semantic-color-interactive-primary-default)',
          pointBackgroundColor: 'var(--semantic-color-interactive-primary-default)',
        }]
      };
    },
  },

  actions: {
    /**
     * Recupera i dati del Vantage Score dal backend e aggiorna lo stato.
     */
    async fetchVantageScore(filters = {}) {
      this.isLoading = true;
      this.error = null;
      const authStore = useAuthStore();
      const userId = authStore.user?.id;

      if (!userId) {
        this.error = 'User not authenticated.';
        this.isLoading = false;
        return;
      }

      try {
        const response = await apiClient.get('/api/v1/trades/vantage-score', {
          params: {
            user_id: userId,
            ...filters,
          },
        });
        this.vantageScore = response.data;
      } catch (err) {
        this.error = 'Failed to fetch Vantage Score data.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
