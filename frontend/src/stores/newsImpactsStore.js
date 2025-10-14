import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

export const useNewsImpactsStore = defineStore('newsImpacts', () => {
  // --- STATE ---
  const newsImpacts = ref([]);
  const newsImpactsGroups = ref([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);

  // --- GETTERS ---
  const groupedNewsImpacts = computed(() => {
    return newsImpactsGroups.value;
  });

  // --- ACTIONS ---
  async function fetchAllNewsImpactsData() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log("User not authenticated. Skipping news impact groups fetch.");
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/me/news-impacts-groups');
      newsImpactsGroups.value = response.data;
    } catch (err) {
      console.error('Error fetching news impact groups:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      newsImpactsGroups.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  return {
    newsImpacts,
    newsImpactsGroups,
    isLoading,
    isSaving,
    error,
    groupedNewsImpacts,
    fetchAllNewsImpactsData,
  };
});