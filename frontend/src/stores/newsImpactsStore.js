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
  const isCreatingGroup = ref(false);
  const creatingTagInGroupId = ref(null);

  // --- ACTIONS ---
  function setCreatingGroup(status) {
    isCreatingGroup.value = status;
  }

  function setCreatingTagInGroup(groupId) {
    creatingTagInGroupId.value = groupId;
  }

  // --- GETTERS ---
  const groupedNewsImpacts = computed(() => {
    if (!newsImpactsGroups.value.length) {
      return [];
    }
    return newsImpactsGroups.value.map(group => ({
      ...group,
      news_impacts: newsImpacts.value.filter(impact => impact.group_id === group.id),
    }));
  });

  // --- ACTIONS ---
  async function fetchNewsImpacts() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;
    try {
      const response = await apiClient.get('/me/news-impacts');
      newsImpacts.value = response.data;
    } catch (err) {
      console.error('Error fetching news impacts:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      newsImpacts.value = [];
    }
  }

  async function fetchNewsImpactsGroups() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;
    try {
      const response = await apiClient.get('/me/news-impacts-groups');
      newsImpactsGroups.value = response.data;
    } catch (err) {
      console.error('Error fetching news impact groups:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      newsImpactsGroups.value = [];
    }
  }

  async function fetchAllNewsImpactsData() {
    if (newsImpacts.value.length > 0 && newsImpactsGroups.value.length > 0) {
      return;
    }
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log("User not authenticated. Skipping all news impacts data fetch.");
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      await Promise.all([fetchNewsImpacts(), fetchNewsImpactsGroups()]);
    } catch (err) {
      console.error('Error fetching all news impacts data:', err);
      error.value = 'An error occurred while fetching news impacts information.';
    } finally {
      isLoading.value = false;
    }
  }

  // --- GROUP ACTIONS ---
  async function createNewsImpactGroup(groupData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.post('/me/news-impacts-groups', groupData);
          await fetchAllNewsImpactsData();
          uiStore.showNotification({ message: 'Group created successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updateNewsImpactGroup(groupId, groupData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/me/news-impacts-groups/${groupId}`, groupData);
          await fetchAllNewsImpactsData();
          uiStore.showNotification({ message: 'Group updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deleteNewsImpactGroup(groupId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/me/news-impacts-groups/${groupId}`);
          await fetchAllNewsImpactsData();
          uiStore.showNotification({ message: 'Group deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- IMPACT ACTIONS ---
  async function createNewsImpact(impactData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          const response = await apiClient.post('/me/news-impacts', impactData);
          await fetchAllNewsImpactsData(); // Refresh the full list
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

  async function updateNewsImpact(impactId, impactData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/me/news-impacts/${impactId}`, impactData);
          await fetchAllNewsImpactsData();
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

  async function deleteNewsImpact(impactId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/me/news-impacts/${impactId}`);
          await fetchAllNewsImpactsData();
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

  return {
    newsImpacts,
    newsImpactsGroups,
    isLoading,
    isSaving,
    error,
    isCreatingGroup,
    creatingTagInGroupId,
    setCreatingGroup,
    setCreatingTagInGroup,
    groupedNewsImpacts,
    fetchAllNewsImpactsData,
    createNewsImpactGroup,
    updateNewsImpactGroup,
    deleteNewsImpactGroup,
    createNewsImpact,
    updateNewsImpact,
    deleteNewsImpact,
  };
});