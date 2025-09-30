import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUiStore = defineStore('ui', () => {
  // --- STATO ---
  const isAppLoading = ref(false);
  const theme = ref('dark'); // o 'light' come default

  // --- AZIONI ---
  function showLoader() {
    isAppLoading.value = true;
  }

  function hideLoader() {
    isAppLoading.value = false;
  }

  function toggleTheme() {
    const newTheme = theme.value === 'light' ? 'dark' : 'light';
    theme.value = newTheme;
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    theme.value = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  // Assicurati che TUTTE le funzioni che vuoi usare altrove
  // siano incluse qui nel return.
  return {
    isAppLoading,
    theme,
    showLoader,  // <-- ESPORTA QUESTA
    hideLoader,  // <-- ESPORTA QUESTA
    toggleTheme,
    initTheme
  };
});