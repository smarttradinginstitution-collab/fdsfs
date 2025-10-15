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
import { useTradingDnaStore } from './tradingDnaStore';

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  const user = ref(null);
  const token = ref(null);
  const generalAccount = ref(null);
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
   * Azione centralizzata per caricare i dati di sessione.
   * Controlla la cache prima di eseguire le chiamate API per evitare
   * caricamenti superflui.
   */
  async function initSessionData() {
    console.log("Inizio caricamento dati di sessione, verificando la cache...");
    const fetchPromises = [];

    const playbookStore = usePlaybookStore();
    if (playbookStore.playbooks.length === 0) {
      console.log("Cache dei playbook vuota, eseguo il fetch...");
      fetchPromises.push(playbookStore.fetchPlaybooks());
    } else {
      console.log("Cache dei playbook piena, dati caricati localmente.");
    }

    const notebookStore = useNotebookStore();
    if (notebookStore.folders.length === 0) {
      console.log("Cache delle cartelle del notebook vuota, eseguo il fetch...");
      fetchPromises.push(notebookStore.fetchFolders());
    } else {
      console.log("Cache delle cartelle del notebook piena, dati caricati localmente.");
    }

    const tagsStore = useTagsStore();
    if (tagsStore.tags.length === 0 || tagsStore.tagGroups.length === 0) {
      console.log("Cache dei tag vuota, eseguo il fetch...");
      fetchPromises.push(tagsStore.fetchAllTagsData());
    } else {
      console.log("Cache dei tag piena, dati caricati localmente.");
    }

    const tradingDnaStore = useTradingDnaStore();
    if (!tradingDnaStore.report) {
      console.log("Cache del report Trading DNA vuota, eseguo il fetch...");
      fetchPromises.push(tradingDnaStore.fetchTradingDnaReport());
    } else {
      console.log("Cache del report Trading DNA piena, dati caricati localmente.");
    }

    if (fetchPromises.length > 0) {
      await Promise.allSettled(fetchPromises);
      console.log("Caricamento dati di sessione dal backend completato.");
    } else {
      console.log("Tutti i dati di sessione sono stati caricati dalla cache.");
    }
  }

  // Funzione per recuperare il General Account
  async function fetchGeneralAccount() {
    try {
      const { data } = await apiClient.get('/general-accounts/me');
      generalAccount.value = data;
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
    await apiClient.post('/auth/register', { name, email, password, confirm_password });
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
    localStorage.clear();
    user.value = null;
    token.value = null;
    generalAccount.value = null;
    mfaChallenge.value = null;
    mfaAal1Token.value = null;
    setAuthToken(null);
    window.location.href = '/login';
  }

  async function initAuth() {
    if (token.value) {
      setAuthToken(token.value);
      if (generalAccount.value) {
        await initSessionData();
      } else {
        await fetchGeneralAccount();
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
}, {
  persist: true,
});
