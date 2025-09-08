// =============================================================================
// FILE: main.js
// DESCRIZIONE: Questo è il punto di ingresso principale dell'intera applicazione.
// È il primo file che viene eseguito e ha il compito di "assemblare"
// le parti fondamentali di Vue e dei suoi plugin.
// =============================================================================

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useAuthStore } from '@/stores/auth'; // (AGGIUNTA) Store di autenticazione per ripristinare il token
import { setAuthToken } from '@/services/api'; // (AGGIUNTA) helper per impostare header Authorization

// --- IMPORTAZIONI DEGLI STILI GLOBALI ---
/*
  BEST PRACTICE: Importazione Centralizzata degli Stili
  Importiamo prima `index.css`, che è il nostro punto di ingresso per tutti i
  design token. A sua volta, `index.css` importa i file dei token nell'ordine
  corretto (`_base.css` e poi `tokens.css`).
  Successivamente importiamo `main.css`, che contiene gli stili globali e i reset,
  e che può quindi utilizzare i token definiti in precedenza.
*/
import '@/styles/index.css';
import '@/assets/main.css';

// --- CREAZIONE E CONFIGURAZIONE DELL'APP ---

// 1. Creiamo l'istanza principale dell'applicazione Vue.
const app = createApp(App);

// 2. Creiamo un'istanza di Pinia (così possiamo anche usarla fuori dai componenti).
const pinia = createPinia();

// 3. Diciamo a Vue di usare Pinia per la gestione dello stato.
app.use(pinia);

// 4. Diciamo a Vue di usare il nostro router per la navigazione.
app.use(router);

// --- INIZIALIZZAZIONE AUTENTICAZIONE (AGGIUNTA) ---
// Ripristina il token dal localStorage e imposta l'header Authorization su apiClient (se presente).
// Va eseguito prima del mount, così tutte le richieste iniziali avranno già l'header corretto.
const auth = useAuthStore(pinia); // <-- passa esplicitamente pinia poiché siamo fuori da setup()
auth.initAuth();                  // imposta Authorization se trova un token salvato

// (opzionale ma sicuro) Forza l'Authorization di axios in caso di token già presente
const stored = localStorage.getItem('token');
if (stored) {
  setAuthToken(stored);
}

// --- MONTAGGIO DELL'APP ---
// 5. Infine, "montiamo" l'applicazione nell'elemento `#app` del DOM.
app.mount('#app');
