import { ref } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const useLabelsStore = defineStore('labels', () => {
  // --- STATE ---
  // Un unico state per contenere tutte le etichette, divise per tipo.
  // Es: { 'mistakes': [], 'psychology-states': [] }
  const labels = ref({});
  const isLoading = ref({}); // Traccia il caricamento per tipo
  const error = ref(null);

  // --- ACTIONS ---
  async function fetchLabelsIfNeeded(labelType) {
    // Se i dati per questo tipo sono già stati caricati, non fare nulla.
    if (labels.value[labelType] && labels.value[labelType].length > 0) {
      return;
    }

    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log(`User not authenticated. Skipping ${labelType} fetch.`);
      return;
    }

    isLoading.value[labelType] = true;
    error.value = null;

    try {
      const response = await apiClient.get(`/me/${labelType}`);
      labels.value[labelType] = response.data;
    } catch (err) {
      console.error(`Error fetching ${labelType}:`, err);
      error.value = err.response?.data?.detail || `An unexpected error occurred while fetching ${labelType}.`;
      labels.value[labelType] = [];
    } finally {
      isLoading.value[labelType] = false;
    }
  }

  // --- EXPORT ---
  return {
    labels,
    isLoading,
    error,
    fetchLabelsIfNeeded,
  };
});