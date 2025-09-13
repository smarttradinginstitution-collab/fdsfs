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
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const mfaRequired = ref(false); // Nuovo stato per gestire il flusso MFA

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value);

  // --- ACTIONS ---
  async function loadCurrentRoleName() {
    try {
      const userId = user.value?.id;
      if (!userId) return;
      const { data } = await apiClient.get(`/api/v1/users/${userId}/roles`);
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

  function setSession(sessionData) {
    const { access_token, user: userData } = sessionData;
    token.value = access_token;
    user.value = userData;
    mfaRequired.value = false; // Reset MFA state on successful login
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setAuthToken(access_token);
    loadCurrentRoleName();
    router.push('/');
  }

  async function login(email, password) {
    mfaRequired.value = false;
    try {
      const response = await apiClient.post('/api/v1/auth/login', {
        email,
        password,
      });
      setSession(response.data);
    } catch (error) {
      if (error.response?.data?.detail?.mfa_required) {
        mfaRequired.value = true;
      } else {
        console.error('Errore durante il login:', error);
        throw error;
      }
    }
  }

  async function loginWithMfa(email, password, code) {
    try {
      const response = await apiClient.post('/api/v1/auth/mfa/login/verify', {
        email,
        password,
        code,
      });
      setSession(response.data);
    } catch (error) {
      console.error('Errore durante il login con MFA:', error);
      throw error;
    }
  }

  async function logout() {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } catch {
      /* noop */
    }

    user.value = null;
    token.value = null;
    mfaRequired.value = false; // Reset on logout

    localStorage.removeItem('token');
    localStorage.removeItem('user');

    setAuthToken(null);

    router.push('/login');
  }

  function initAuth() {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      token.value = storedToken;
      setAuthToken(storedToken);
    }

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
  return {
    user,
    token,
    isAuthenticated,
    mfaRequired,
    login,
    loginWithMfa,
    logout,
    initAuth,
  };
});
