// =============================================================================
// FILE: main.js
// DESCRIZIONE: Questo è il punto di ingresso principale dell'intera applicazione.
// È il primo file che viene eseguito e ha il compito di "assemblare"
// le parti fondamentali di Vue e dei suoi plugin.
// =============================================================================

// --- IMPORTAZIONI FONDAMENTALI ---
// Qui importiamo le librerie e i file necessari per avviare l'applicazione.

// `createApp` è la funzione di Vue 3 per creare una nuova istanza dell'applicazione.
import { createApp } from 'vue';

// `createPinia` è la funzione per creare l'istanza di Pinia, il nostro gestore di stato.
import { createPinia } from 'pinia';

// `App` è il componente Vue principale, il "guscio" che contiene tutta l'interfaccia.
import App from './App.vue';

// `router` è la nostra configurazione di Vue Router, che gestisce le pagine e la navigazione.
import router from './router';


// --- IMPORTAZIONI DEGLI STILI GLOBALI ---
// Questi file CSS vengono importati qui per essere disponibili in tutta l'applicazione.

// `index.css` è il nuovo punto di ingresso per tutti i design token.
// Importa sia i token di base che quelli semantici nell'ordine corretto.
import './styles/index.css';

// `main.css` contiene stili CSS globali o reset di base.
// Viene importato dopo i token in modo da poterli utilizzare.
import './assets/main.css';


// --- CREAZIONE E CONFIGURAZIONE DELL'APP ---

// 1. Creiamo l'istanza principale dell'applicazione Vue, usando il nostro componente `App.vue` come base.
const app = createApp(App);

// 2. Diciamo a Vue di usare Pinia. Da questo momento, possiamo usare gli "stores" in qualsiasi componente.
app.use(createPinia());

// 3. Diciamo a Vue di usare il nostro router. Ora l'applicazione può gestire diverse pagine (rotte).
app.use(router);


// --- MONTAGGIO DELL'APP ---

// 4. Infine, "montiamo" l'applicazione. Vue prende tutto quello che abbiamo costruito
//    e lo inserisce nell'elemento HTML con `id="app"` che si trova nel file `index.html`.
//    Da questo momento, l'applicazione è visibile e interattiva nel browser.
app.mount('#app');
