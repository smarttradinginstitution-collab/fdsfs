// =============================================================================
// FILE: src/stores/auth.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato di autenticazione
// dell'applicazione. Si occupa di login, logout, e di persistere lo stato
// dell'utente e il token JWT nel localStorage.
// =============================================================================
import { defineStore } from 'pinia';
import { ref, computed }from 'vue';
import apiClient from '@/services/api';
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  // Usiamo ref per definire lo stato reattivo.
  // Lo stato viene inizializzato dal localStorage per mantenere l'utente
  // loggato tra le sessioni.
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);

  // --- GETTERS ---
  // I getters sono come le computed properties per gli store.
  const isAuthenticated = computed(() => !!token.value);

  // --- ACTIONS ---
  // Le azioni sono metodi che possono essere chiamati per modificare lo stato.

  /**
   * Esegue il login dell'utente.
   * @param {string} email - L'email dell'utente.
   * @param {string} password - La password dell'utente.
   */
  async function login(email, password) {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      });

      const { access_token, user: userData } = response.data;

      // Aggiorna lo stato dello store
      token.value = access_token;
      user.value = userData;

      // Salva il token e i dati utente nel localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Imposta il token nell'header di apiClient per le richieste future
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Reindirizza al dashboard dopo il login
      router.push('/');
    } catch (error) {
      console.error("Errore durante il login:", error);
      // Rilancia l'errore per poterlo gestire nel componente UI
      throw error;
    }
  }

  /**
   * Esegue il logout dell'utente.
   */
  function logout() {
    // Rimuovi i dati dallo stato
    user.value = null;
    token.value = null;

    // Rimuovi i dati dal localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Rimuovi l'header di autorizzazione da apiClient
    delete apiClient.defaults.headers.common['Authorization'];

    // Reindirizza alla pagina di login
    router.push('/login');
  }

  /**
   * Inizializza il token di autorizzazione se presente nel localStorage
   */
  function initAuth() {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      token.value = storedToken;
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
  }


  // --- EXPORT ---
  // Esponiamo lo stato e le azioni per renderli accessibili
  // ai componenti che useranno questo store.
  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    initAuth,
  };
});
