import { ref } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useUiStore } from './uiStore';

export const useNewsImpactsStore = defineStore('newsImpacts', () => {
  // --- STATE ---
  const newsImpacts = ref([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  async function fetchAllNewsImpacts() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/me/news-impacts');
      newsImpacts.value = response.data;
    } catch (err) {
      console.error('Error fetching news impacts:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      newsImpacts.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewsImpact(newsImpactData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          const response = await apiClient.post('/me/news-impacts', newsImpactData);
          await fetchAllNewsImpacts(); // Refresh the list
          uiStore.showNotification({ message: 'News impact created successfully.', type: 'success' });
          return response.data;
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create news impact.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updateNewsImpact(newsImpactId, newsImpactData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/news-impacts/${newsImpactId}`, newsImpactData);
          await fetchAllNewsImpacts(); // Refresh the list
          uiStore.showNotification({ message: 'News impact updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update news impact.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deleteNewsImpact(newsImpactId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/news-impacts/${newsImpactId}`);
          await fetchAllNewsImpacts(); // Refresh the list
          uiStore.showNotification({ message: 'News impact deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete news impact.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- EXPORT ---
  return {
    newsImpacts,
    isLoading,
    isSaving,
    error,
    fetchAllNewsImpacts,
    createNewsImpact,
    updateNewsImpact,
    deleteNewsImpact,
  };
});