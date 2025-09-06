import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isLoading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    setAuthData(user, token) {
      this.user = user;
      this.token = token;
      localStorage.setItem('token', token);
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    clearAuthData() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('token');
      delete apiClient.defaults.headers.common['Authorization'];
    },

    async login(credentials) {
      this.isLoading = true;
      try {
        // 1. Endpoint corretto
        const response = await apiClient.post('/api/v1/auth/login', credentials);

        // 2. Parsing della risposta flat
        const { user, access_token } = response.data;
        if (!access_token || !user) {
          throw new Error('Login response is missing access_token or user.');
        }

        this.setAuthData(user, access_token);
      } catch (error) {
        this.clearAuthData();
        // Rilancia l'errore per permettere al componente di gestirlo (es. mostrare un messaggio)
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    logout() {
      this.clearAuthData();
      // Optionally, you could also call a backend endpoint to invalidate the token
    },

    async checkAuth() {
      if (!this.token) {
        return;
      }
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      try {
        const response = await apiClient.get('/api/v1/users/me');
        this.user = response.data;
      } catch (error) {
        this.clearAuthData();
      }
    },
  },
});
