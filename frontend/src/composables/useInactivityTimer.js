// =============================================================================
// FILE: src/composables/useInactivityTimer.js
// DESCRIZIONE: Composable di Vue 3 per rilevare l'inattività dell'utente.
//              Esegue una callback dopo un determinato periodo di tempo senza
//              interazioni da parte dell'utente (mouse, tastiera, ecc.).
// =============================================================================

import { onUnmounted } from 'vue';

/**
 * Hook composable per monitorare l'inattività dell'utente.
 *
 * @param {function} onTimeout - La funzione da eseguire quando il timer scade.
 * @param {number} [timeoutInSeconds=30] - Il tempo di inattività in secondi.
 * @returns {{start: function, stop: function}} - Oggetto con funzioni per avviare e fermare il timer.
 */
export function useInactivityTimer(onTimeout, timeoutInSeconds = 30) {
  let timer = null;

  // Lista di eventi che indicano attività dell'utente
  const userActivityEvents = [
    'mousemove',
    'mousedown',
    'keypress',
    'scroll',
    'touchstart',
  ];

  /**
   * Resetta il timer di inattività.
   * Viene chiamato ogni volta che viene rilevata un'attività dell'utente.
   */
  const resetTimer = () => {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      onTimeout();
    }, timeoutInSeconds * 1000);
  };

  /**
   * Avvia il monitoraggio dell'inattività.
   * Aggiunge gli event listener e avvia il timer per la prima volta.
   */
  const start = () => {
    userActivityEvents.forEach(event =>
      window.addEventListener(event, resetTimer)
    );
    resetTimer(); // Avvia il timer al momento dell'attivazione
  };

  /**
   * Ferma il monitoraggio dell'inattività.
   * Rimuove gli event listener e cancella il timer.
   */
  const stop = () => {
    if (timer) {
      clearTimeout(timer);
    }
    userActivityEvents.forEach(event =>
      window.removeEventListener(event, resetTimer)
    );
  };

  // Assicura che il timer e gli listener vengano rimossi quando il componente
  // che usa questo hook viene smontato, per prevenire memory leak.
  onUnmounted(() => {
    stop();
  });

  return {
    start,
    stop,
  };
}