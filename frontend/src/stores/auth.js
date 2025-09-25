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
import { useAccountStore } from './account';
import { useResourceStore } from './resourceStore';

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const mfaChallenge = ref(null);
  const mfaAal1Token = ref(null); // Token temporaneo AAL1 per la verifica

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value);
  const isMfaActive = computed(() => user.value?.factors?.some(f => f.factor_type === 'totp' && f.status === 'verified'));
  const getMfaFactor = computed(() => {
    if (!isMfaActive.value) return null;
    return user.value.factors.find(f => f.factor_type === 'totp' && f.status === 'verified');
  });

  // --- ACTIONS ---
  async function _setAuthentication(accessToken, userData) {
    token.value = accessToken;
    user.value = userData;
    mfaChallenge.value = null;
    mfaAal1Token.value = null;

    localStorage.setItem('token', accessToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setAuthToken(accessToken);

    // Inizializza gli account e le risorse correlate
    const accountStore = useAccountStore();
    await accountStore.initializeAccounts();
    const resourceStore = useResourceStore();
    await resourceStore.fetchAllResources();
  }

  // Carica il nome del ruolo dell'utente. Funzione di supporto.
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

  async function login(email, password) {
    const response = await apiClient.post('/api/v1/auth/login', { email, password });

    if (response.data.status === 'mfa_required') {
      mfaChallenge.value = response.data; // Salva tutta la challenge
      mfaAal1Token.value = response.data.access_token;
      return { mfaRequired: true };
    } else {
      await _setAuthentication(response.data.access_token, response.data.user);
      await loadCurrentRoleName();
      router.push('/');
      return { mfaRequired: false };
    }
  }

  async function verifyMfaAndLogin(otpCode) {
    if (!mfaChallenge.value || !mfaAal1Token.value) throw new Error("Dati della challenge MFA non trovati.");

    const response = await apiClient.post('/api/v1/auth/mfa/verify', {
      access_token: mfaAal1Token.value,
      factor_id: mfaChallenge.value.factor_id,
      challenge_id: mfaChallenge.value.challenge_id,
      code: otpCode,
    });

    await _setAuthentication(response.data.access_token, response.data.user);
    await loadCurrentRoleName();
    router.push('/');
  }

  async function enrollMfa() {
    const { data } = await apiClient.post('/api/v1/auth/mfa/enroll-totp');
    return data;
  }

  async function verifyAndEnableMfa(factorId, challengeId, otpCode) {
    const { data } = await apiClient.post('/api/v1/auth/mfa/verify', {
      access_token: token.value,
      factor_id: factorId,
      challenge_id: challengeId,
      code: otpCode,
    });
    await _setAuthentication(data.access_token, data.user);
    await loadCurrentRoleName();
  }

  async function unenrollMfa(factorId) {
    // Non fa nulla allo stato locale, serve solo per pulizia.
    // L'utente non è autenticato con questo fattore, quindi non c'è bisogno di aggiornare lo stato.
    try {
      await apiClient.delete(`/api/v1/auth/mfa/factors/${factorId}`);
    } catch (error) {
      console.error(`Pulizia del fattore ${factorId} fallita:`, error);
    }
  }

  async function disableMfa(otpCode) {
    const { data } = await apiClient.post('/api/v1/auth/mfa/disable', { code: otpCode });
    await _setAuthentication(data.access_token, data.user);
    await loadCurrentRoleName();
  }

  async function logout() {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } catch { /* noop */ }

    // Resetta gli store degli account e delle risorse
    const accountStore = useAccountStore();
    accountStore.reset();
    const resourceStore = useResourceStore();
    resourceStore.reset();

    user.value = null;
    token.value = null;
    mfaChallenge.value = null;
    mfaAal1Token.value = null;
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
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser);
      } catch {
        localStorage.removeItem('user');
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isMfaActive,
    getMfaFactor,
    mfaChallenge,
    mfaAal1Token,
    login,
    logout,
    initAuth,
    verifyMfaAndLogin,
    enrollMfa,
    verifyAndEnableMfa,
    disableMfa,
    unenrollMfa,
  };
});
