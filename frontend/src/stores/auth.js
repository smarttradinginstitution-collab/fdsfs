// =============================================================================
// FILE: src/stores/auth.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato di autenticazione
// dell'applicazione. Si occupa di login, logout, e di persistere lo stato
// dell'utente e il token JWT nel localStorage.
// =============================================================================
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient, { setAuthToken } from '@/services/api';
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
  // (AGGIUNTA) Carica il nome del ruolo e lo salva in user.roleName
  async function loadCurrentRoleName() {
    try {
      const userId = user.value?.id;
      if (!userId) return;
      // ✅ Endpoint corretto: /api/v1/users/{user_id}/roles
      const { data } = await apiClient.get(`/api/v1/users/${userId}/roles`);
      // Può tornare un oggetto singolo o una lista: gestiamo entrambi i casi
      const roleObj = Array.isArray(data) ? data[0] : data;
      const name = roleObj?.name ?? null;
      if (name) {
        user.value = { ...user.value, roleName: name };
        localStorage.setItem('user', JSON.stringify(user.value));
      }
    } catch (err) {
      console.error('Errore caricamento ruolo:', err);
    }
  }

  /**
   * Esegue il login dell'utente.
   * @param {string} email - L'email dell'utente.
   * @param {string} password - La password dell'utente.
   */
  async function login(email, password) {
    try {
      const response = await apiClient.post('/api/v1/auth/login', {
        email,
        password,
      });

      // (AGGIUNTA) La API può restituire anche token_type/expires_in.
      // Qui ci servono solo access_token e user.
      const { access_token, user: userData } = response.data;

      // Aggiorna lo stato dello store
      token.value = access_token;
      user.value = userData;

      // Salva il token e i dati utente nel localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Imposta il token nell'header di apiClient per le richieste future
      // (AGGIUNTA) Usa l'helper centralizzato per coerenza con gli interceptor
      setAuthToken(access_token);

      // (AGGIUNTA) Popola user.roleName tramite /users/{id}/roles
      await loadCurrentRoleName();

      // Reindirizza al dashboard dopo il login
      router.push('/');
    } catch (error) {
      console.error('Errore durante il login:', error);
      // Rilancia l'errore per poterlo gestire nel componente UI
      throw error;
    }
  }

  /**
   * Esegue il logout dell'utente.
   */
  async function logout() {
    try {
      // (AGGIUNTA) Prova a notificare il backend per invalidare i refresh token lato server.
      // Non blocca il logout lato client in caso di errore.
      await apiClient.post('/api/v1/auth/logout');
    } catch {
      /* noop */
    }

    // Rimuovi i dati dallo stato
    user.value = null;
    token.value = null;

    // Rimuovi i dati dal localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Rimuovi l'header di autorizzazione da apiClient
    // (AGGIUNTA) Usa l'helper centralizzato per rimuovere l'Authorization
    setAuthToken(null);

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
      // (AGGIUNTA) Imposta l'Authorization centralmente
      setAuthToken(storedToken);
    }

    // (AGGIUNTA) Ripristina anche l'utente se presente
    const storedUser = localStorage.getItem('user');
    if (storedUser && !user.value) {
      try {
        user.value = JSON.parse(storedUser);
      } catch {
        localStorage.removeItem('user');
      }
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
