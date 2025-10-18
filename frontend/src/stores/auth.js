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
import { useUiStore } from './uiStore';
import { usePlaybookStore } from './playbookStore';
import { useNotebookStore } from './notebookStore';
import { useTagsStore } from './tagsStore';
import { useTradesStore } from './trades';

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const generalAccount = ref(JSON.parse(localStorage.getItem('generalAccount')) || null);
  const mfaChallenge = ref(null);
  const mfaAal1Token = ref(null);

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value && !!generalAccount.value);
  const isMfaActive = computed(() => user.value?.factors?.some(f => f.factor_type === 'totp' && f.status === 'verified'));
  const getMfaFactor = computed(() => {
    if (!isMfaActive.value) return null;
    return user.value.factors.find(f => f.factor_type === 'totp' && f.status === 'verified');
  });

  // --- ACTIONS ---

  /**
   * Azione centralizzata per caricare tutti i dati di sessione globali
   * dopo che l'autenticazione è stata confermata.
   */
  async function initSessionData() {
    const notebookStore = useNotebookStore();
    const tradesStore = useTradesStore();
    const playbookStore = usePlaybookStore();
    const tagsStore = useTagsStore();

    // Carica tutti i dati di sessione globali in parallelo
    await Promise.allSettled([
      playbookStore.fetchPlaybooks(),
      tagsStore.fetchAllTagsData(),
      notebookStore.fetchFolders(),
      notebookStore.fetchAllNotes(),
      tradesStore.fetchTrades({ ignoreFilters: true }),
    ]);
  }

  // Funzione per recuperare il General Account
  async function fetchGeneralAccount() {
    try {
      const { data } = await apiClient.get('/general-accounts/me');
      generalAccount.value = data;
      localStorage.setItem('generalAccount', JSON.stringify(data));

      // Una volta ottenuto il GA, avvia il caricamento dei dati di sessione.
      await initSessionData();

      return true;
    } catch (error) {
      console.error('Errore nel recupero del General Account:', error);
      await logout();
      return false;
    }
  }

  async function _setAuthentication(accessToken, userData) {
    token.value = accessToken;
    user.value = userData;
    mfaChallenge.value = null;
    mfaAal1Token.value = null;

    localStorage.setItem('token', accessToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setAuthToken(accessToken);

    return await fetchGeneralAccount();
  }

  async function loadCurrentRoleName() {
    try {
      const userId = user.value?.id;
      if (!userId) return;
      const { data } = await apiClient.get(`/users/${userId}/roles`);
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
    const response = await apiClient.post('/auth/login', { email, password });

    if (response.data.status === 'mfa_required') {
      mfaChallenge.value = response.data;
      mfaAal1Token.value = response.data.access_token;
      return { mfaRequired: true };
    } else {
      const authSuccessful = await _setAuthentication(response.data.access_token, response.data.user);
      if (authSuccessful) {
        const uiStore = useUiStore();
        uiStore.setInitialLoadPending(true);
        await loadCurrentRoleName();
        router.push('/select-account');
      }
      return { mfaRequired: false };
    }
  }

  async function register(name, email, password, confirm_password) {
    await apiClient.post('/auth/register', {
      name,
      email,
      password,
      confirm_password,
    });
  }

  async function verifyMfaAndLogin(otpCode) {
    if (!mfaChallenge.value || !mfaAal1Token.value) throw new Error("Dati della challenge MFA non trovati.");

    const response = await apiClient.post('/auth/mfa/verify', {
      access_token: mfaAal1Token.value,
      factor_id: mfaChallenge.value.factor_id,
      challenge_id: mfaChallenge.value.challenge_id,
      code: otpCode,
    });

    const authSuccessful = await _setAuthentication(response.data.access_token, response.data.user);
    if (authSuccessful) {
      const uiStore = useUiStore();
      uiStore.setInitialLoadPending(true);
      await loadCurrentRoleName();
      router.push('/select-account');
    }
  }

  async function enrollMfa() {
    const { data } = await apiClient.post('/auth/mfa/enroll-totp');
    return data;
  }

  async function verifyAndEnableMfa(factorId, challengeId, otpCode) {
    const { data } = await apiClient.post('/auth/mfa/verify', {
      access_token: token.value,
      factor_id: factorId,
      challenge_id: challengeId,
      code: otpCode,
    });
    const authSuccessful = await _setAuthentication(data.access_token, data.user);
    if (authSuccessful) {
      await loadCurrentRoleName();
    }
  }

  async function unenrollMfa(factorId) {
    try {
      await apiClient.delete(`/auth/mfa/factors/${factorId}`);
    } catch (error) {
      console.error(`Pulizia del fattore ${factorId} fallita:`, error);
    }
  }

  async function disableMfa(otpCode) {
    const { data } = await apiClient.post('/auth/mfa/disable', { code: otpCode });
    const authSuccessful = await _setAuthentication(data.access_token, data.user);
    if (authSuccessful) {
      await loadCurrentRoleName();
    }
  }

  async function logout() {
    try {
      await apiClient.post('/auth/logout');
    } catch { /* noop */ }

    const uiStore = useUiStore();
    uiStore.setInitialLoadPending(false);

    user.value = null;
    token.value = null;
    generalAccount.value = null;
    mfaChallenge.value = null;
    mfaAal1Token.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('generalAccount');
    setAuthToken(null);
    router.push('/login');
  }

  async function initAuth() {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      token.value = storedToken;
      setAuthToken(storedToken);
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser);
          await fetchGeneralAccount();
        } catch {
          await logout();
        }
      } else {
        await logout();
      }
    }
  }

  return {
    user,
    token,
    generalAccount,
    isAuthenticated,
    isMfaActive,
    getMfaFactor,
    mfaChallenge,
    mfaAal1Token,
    login,
    register,
    logout,
    initAuth,
    initSessionData,
    verifyMfaAndLogin,
    enrollMfa,
    verifyAndEnableMfa,
    disableMfa,
    unenrollMfa,
  };
});