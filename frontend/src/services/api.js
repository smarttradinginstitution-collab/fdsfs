// =============================================================================
// FILE: src/services/api.js
// =============================================================================
import axios from 'axios';

const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`, // es: "http://127.0.0.1:8000/api/v1"
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

// --- Interceptor richiesta: garantisce Authorization anche se mancasse ---
// (pesca dal localStorage se non è già presente sui defaults)
apiClient.interceptors.request.use((config) => {
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
