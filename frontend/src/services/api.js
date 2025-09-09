// =============================================================================
// FILE: src/services/api.js
// =============================================================================
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // es: "http://127.0.0.1:8000"
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Helper per impostare/rimuovere l'Authorization su apiClient ---
export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
}

// --- Interceptor richiesta: garantisce Authorization e aggiunge il Timezone ---
apiClient.interceptors.request.use((config) => {
  // Aggiunge il fuso orario IANA dell'utente (es. "Europe/Rome") a ogni richiesta.
  // Il backend lo userà per i calcoli timezone-aware.
  config.headers['X-Timezone'] = Intl.DateTimeFormat().resolvedOptions().timeZone;

  // Garantisce che il token di autorizzazione sia presente se disponibile.
  if (!config.headers.Authorization) {
    const stored = localStorage.getItem('token');
    if (stored) {
      config.headers.Authorization = `Bearer ${stored}`;
    }
  }
  return config;
});

// --- Interceptor risposta: logga 401/403 per capire subito l’origine ---
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response) {
      console.warn(
        '[API ERROR]',
        err.response.status,
        err.response.data || err.response.statusText
      );
    } else {
      console.warn('[API ERROR]', err.message);
    }
    return Promise.reject(err);
  }
);

export default apiClient;
