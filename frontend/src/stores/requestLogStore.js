import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import requestLogService from '@/services/requestLogService';
import { useUiStore } from './uiStore';

export const useRequestLogStore = defineStore('requestLog', () => {
  // --- STATE ---
  const logs = ref([]);
  const isLoading = ref(false);

  const pagination = reactive({
    offset: 0,
    limit: 25,
    total: 0,
  });

  const sorting = reactive({
    by: 'created_at',
    order: 'desc',
  });

  const filters = reactive({
    statusCode: null,
  });

  // --- ACTIONS ---

  /**
   * Recupera i log dal backend in base allo stato corrente di filtri,
   * ordinamento e paginazione.
   */
  async function fetchRequestLogs() {
    isLoading.value = true;
    const uiStore = useUiStore();
    try {
      const params = {
        offset: pagination.offset,
        limit: pagination.limit,
        sort_by: sorting.by,
        sort_order: sorting.order,
        status_code_filter: filters.statusCode,
      };

      // Rimuovi i filtri nulli o vuoti
      Object.keys(params).forEach(key => {
        if (params[key] === null || params[key] === '') {
          delete params[key];
        }
      });

      const response = await requestLogService.getRequestLogs(params);
      logs.value = response.data.data;
      pagination.total = response.data.total;

    } catch (error) {
      console.error('Errore nel recupero dei log delle richieste:', error);
      uiStore.showToast({ message: 'Impossibile caricare i log.', type: 'danger' });
      logs.value = [];
      pagination.total = 0;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Cambia la pagina corrente e ricarica i dati.
   * @param {number} newOffset - Il nuovo offset per la paginazione.
   */
  function changePage(newOffset) {
    pagination.offset = newOffset;
    return fetchRequestLogs();
  }

  /**
   * Cambia l'ordinamento e ricarica i dati.
   * @param {string} newSortBy - La colonna per cui ordinare.
   */
  function changeSort(newSortBy) {
    if (sorting.by === newSortBy) {
      sorting.order = sorting.order === 'asc' ? 'desc' : 'asc';
    } else {
      sorting.by = newSortBy;
      sorting.order = 'desc';
    }
    pagination.offset = 0; // Torna alla prima pagina
    return fetchRequestLogs();
  }

  /**
   * Applica un filtro e ricarica i dati.
   * @param {number | null} statusCode - Il codice di stato da filtrare.
   */
  function applyFilter(statusCode) {
    filters.statusCode = statusCode;
    pagination.offset = 0; // Torna alla prima pagina
    return fetchRequestLogs();
  }

  /**
   * Cancella tutti i log dal backend e ricarica la vista.
   */
  async function clearAllLogs() {
    const uiStore = useUiStore();
    if (!confirm('Sei sicuro di voler cancellare tutti i log delle richieste? L\'azione è irreversibile.')) {
      return;
    }

    isLoading.value = true;
    try {
      await requestLogService.clearRequestLogs();
      uiStore.showToast({ message: 'Tutti i log sono stati cancellati con successo.', type: 'success' });
      // Ricarica i dati (che ora saranno vuoti)
      await fetchRequestLogs();
    } catch (error) {
      console.error('Errore nella cancellazione dei log:', error);
      uiStore.showToast({ message: 'Impossibile cancellare i log.', type: 'danger' });
    } finally {
      isLoading.value = false;
    }
  }

  return {
    logs,
    isLoading,
    pagination,
    sorting,
    filters,
    fetchRequestLogs,
    changePage,
    changeSort,
    applyFilter,
    clearAllLogs,
  };
});