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
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const generalAccount = ref(JSON.parse(localStorage.getItem('generalAccount')) || null); // Nuovo state per il General Account
  const mfaChallenge = ref(null);
  const mfaAal1Token = ref(null); // Token temporaneo AAL1 per la verifica

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value && !!generalAccount.value); // L'utente è autenticato solo se ha anche un General Account
  const isMfaActive = computed(() => user.value?.factors?.some(f => f.factor_type === 'totp' && f.status === 'verified'));
  const getMfaFactor = computed(() => {
    if (!isMfaActive.value) return null;
    return user.value.factors.find(f => f.factor_type === 'totp' && f.status === 'verified');
  });

  // --- ACTIONS ---

  /**
   * Azione centralizzata per caricare tutti i dati di sessione necessari
   * dopo che l'autenticazione è stata confermata.
   */
  async function initSessionData() {
    console.log('%c[AuthStore] Inizio initSessionData (Gruppo 3)...', 'color: purple;');
    // Carica i dati di sessione del Gruppo 3
    await Promise.allSettled([
      usePlaybookStore().fetchPlaybooks(),
      useTagsStore().fetchAllTagsData(),
      useTradingDnaStore().fetchTradingDnaReport(),
    ]);
    console.log('%c[AuthStore] Completato initSessionData.', 'color: purple;');
  }

  // Funzione per recuperare il General Account
  async function fetchGeneralAccount() {
    try {
      const { data } = await apiClient.get('/general-accounts/me');
      generalAccount.value = data;
      localStorage.setItem('generalAccount', JSON.stringify(data));

      // Il caricamento dei dati di sessione verrà ora gestito dalla DashboardView.
      // await initSessionData();

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

    // Dopo aver impostato il token, recupera il General Account
    return await fetchGeneralAccount();
  }

  // Carica il nome del ruolo dell'utente. Funzione di supporto.
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
      mfaChallenge.value = response.data; // Salva tutta la challenge
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
    // Dopo la registrazione, non facciamo il login automatico.
    // La vista reindirizzerà alla pagina di login con un messaggio.
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
    // Qui non facciamo il redirect, ma aggiorniamo lo stato
    const authSuccessful = await _setAuthentication(data.access_token, data.user);
    if (authSuccessful) {
      await loadCurrentRoleName();
    }
  }

  async function unenrollMfa(factorId) {
    // Non fa nulla allo stato locale, serve solo per pulizia.
    // L'utente non è autenticato con questo fattore, quindi non c'è bisogno di aggiornare lo stato.
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
    generalAccount.value = null; // Pulisci il General Account
    mfaChallenge.value = null;
    mfaAal1Token.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('generalAccount'); // Rimuovi dal localStorage
    setAuthToken(null);
    router.push('/login');
  }

  async function initAuth() {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      token.value = storedToken;
      setAuthToken(storedToken);
      // Se c'è un token, proviamo a recuperare i dati dell'utente e del GA
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser);
          // Tentativo di recuperare il General Account all'avvio
          await fetchGeneralAccount();
        } catch {
          // Se qualcosa va storto, puliamo tutto
          await logout();
        }
      } else {
        await logout(); // Se non ci sono dati utente, il token è invalido
      }
    }
  }

  return {
    user,
    token,
    generalAccount, // Esponi il nuovo state
    isAuthenticated,
    isMfaActive,
    getMfaFactor,
    mfaChallenge,
    mfaAal1Token,
    login,
    register,
    logout,
    initAuth,
    initSessionData, // Esponi la nuova azione
    verifyMfaAndLogin,
    enrollMfa,
    verifyAndEnableMfa,
    disableMfa,
    unenrollMfa,
  };
});
