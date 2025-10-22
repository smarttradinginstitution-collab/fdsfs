import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useUiStore } from './uiStore';
import { useNewsImpactsStore } from './newsImpactsStore';

export const useLibraryStore = defineStore('library', () => {
  // --- STATE ---
  const mistakes = ref([]);
  const psychologyStates = ref([]);
  const newsImpactsStore = useNewsImpactsStore();

  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);

  // --- COMPUTED ---
  const newsImpacts = computed(() => newsImpactsStore.groupedNewsImpacts);

  // --- PRIVATE FETCH ACTIONS ---
  async function fetchMistakes() {
    const response = await apiClient.get('/me/mistakes');
    mistakes.value = response.data;
  }

  async function fetchPsychologyStates() {
    const response = await apiClient.get('/me/psychology-states');
    psychologyStates.value = response.data;
  }

  // --- PUBLIC ACTIONS ---
  async function fetchAllLibraryData() {
    isLoading.value = true;
    error.value = null;
    try {
      await Promise.all([
        fetchMistakes(),
        fetchPsychologyStates(),
        newsImpactsStore.fetchAllNewsImpactsData(),
      ]);
    } catch (err) {
      console.error('Error fetching library data:', err);
      const errorMessage = err.response?.data?.detail || 'An unexpected error occurred while fetching library data.';
      error.value = errorMessage;
      useUiStore().showNotification({ message: errorMessage, type: 'error' });
    } finally {
      isLoading.value = false;
    }
  }

  // --- GENERIC CRUD FUNCTION ---
  async function performCrudOperation(operation, entityName, entityId = null, data = null) {
    const uiStore = useUiStore();
    isSaving.value = true;
    error.value = null;

    const endpointMap = {
      mistake: 'mistakes',
      psychologyState: 'psychology-states',
    };
    const entityUrlName = endpointMap[entityName];

    try {
      let response;
      let successMessage = '';

      switch (operation) {
        case 'create':
          response = await apiClient.post(`/me/${entityUrlName}`, data);
          successMessage = `${entityName.replace(/([A-Z])/g, ' $1')} created successfully.`;
          break;
        case 'update':
          response = await apiClient.put(`/${entityUrlName}/${entityId}`, data);
          successMessage = `${entityName.replace(/([A-Z])/g, ' $1')} updated successfully.`;
          break;
        case 'delete':
          response = await apiClient.delete(`/${entityUrlName}/${entityId}`);
          successMessage = `${entityName.replace(/([A-Z])/g, ' $1')} deleted successfully.`;
          break;
      }

      await fetchAllLibraryData();
      uiStore.showNotification({ message: successMessage, type: 'success' });
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || `Failed to ${operation} ${entityName}.`;
      error.value = errorMessage;
      uiStore.showNotification({ message: errorMessage, type: 'error' });
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  // --- EXPORTS ---
  return {
    mistakes,
    psychologyStates,
    newsImpacts,
    isLoading,
    isSaving,
    error,
    fetchAllLibraryData,

    // Mistakes
    createMistake: (data) => performCrudOperation('create', 'mistake', null, data),
    updateMistake: (id, data) => performCrudOperation('update', 'mistake', id, data),
    deleteMistake: (id) => performCrudOperation('delete', 'mistake', id),

    // Psychology States
    createPsychologyState: (data) => performCrudOperation('create', 'psychologyState', null, data),
    updatePsychologyState: (id, data) => performCrudOperation('update', 'psychologyState', id, data),
    deletePsychologyState: (id) => performCrudOperation('delete', 'psychologyState', id),

    resetState,
  };

  function resetState() {
    mistakes.value = [];
    psychologyStates.value = [];
    isLoading.value = false;
    isSaving.value = false;
    error.value = null;
  }
});