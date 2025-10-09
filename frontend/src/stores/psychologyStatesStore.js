import { ref } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useUiStore } from './uiStore';

export const usePsychologyStatesStore = defineStore('psychologyStates', () => {
  // --- STATE ---
  const psychologyStates = ref([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  async function fetchAllPsychologyStates() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/me/psychology-states');
      psychologyStates.value = response.data;
    } catch (err) {
      console.error('Error fetching psychology states:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      psychologyStates.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function createPsychologyState(psychologyStateData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          const response = await apiClient.post('/me/psychology-states', psychologyStateData);
          await fetchAllPsychologyStates(); // Refresh the list
          uiStore.showNotification({ message: 'Psychology state created successfully.', type: 'success' });
          return response.data;
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create psychology state.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updatePsychologyState(psychologyStateId, psychologyStateData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/psychology-states/${psychologyStateId}`, psychologyStateData);
          await fetchAllPsychologyStates(); // Refresh the list
          uiStore.showNotification({ message: 'Psychology state updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update psychology state.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deletePsychologyState(psychologyStateId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/psychology-states/${psychologyStateId}`);
          await fetchAllPsychologyStates(); // Refresh the list
          uiStore.showNotification({ message: 'Psychology state deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete psychology state.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- EXPORT ---
  return {
    psychologyStates,
    isLoading,
    isSaving,
    error,
    fetchAllPsychologyStates,
    createPsychologyState,
    updatePsychologyState,
    deletePsychologyState,
  };
});