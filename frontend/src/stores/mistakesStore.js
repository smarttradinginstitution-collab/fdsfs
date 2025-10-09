import { ref } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useUiStore } from './uiStore';

export const useMistakesStore = defineStore('mistakes', () => {
  // --- STATE ---
  const mistakes = ref([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  async function fetchAllMistakes() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/me/mistakes');
      mistakes.value = response.data;
    } catch (err) {
      console.error('Error fetching mistakes:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      mistakes.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function createMistake(mistakeData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          const response = await apiClient.post('/me/mistakes', mistakeData);
          await fetchAllMistakes(); // Refresh the list
          uiStore.showNotification({ message: 'Mistake created successfully.', type: 'success' });
          return response.data;
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create mistake.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updateMistake(mistakeId, mistakeData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/mistakes/${mistakeId}`, mistakeData);
          await fetchAllMistakes(); // Refresh the list
          uiStore.showNotification({ message: 'Mistake updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update mistake.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deleteMistake(mistakeId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/mistakes/${mistakeId}`);
          await fetchAllMistakes(); // Refresh the list
          uiStore.showNotification({ message: 'Mistake deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete mistake.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- EXPORT ---
  return {
    mistakes,
    isLoading,
    isSaving,
    error,
    fetchAllMistakes,
    createMistake,
    updateMistake,
    deleteMistake,
  };
});