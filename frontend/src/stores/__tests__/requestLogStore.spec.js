import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useRequestLogStore } from '../requestLogStore';
import requestLogService from '@/services/requestLogService';

// Mock del servizio API
vi.mock('@/services/requestLogService', () => ({
  default: {
    getRequestLogs: vi.fn(),
    clearRequestLogs: vi.fn(),
  },
}));

// Mock dello store UI per evitare errori di dipendenza
vi.mock('@/stores/uiStore', () => ({
  useUiStore: () => ({
    showToast: vi.fn(),
  }),
}));


describe('RequestLog Store', () => {
  beforeEach(() => {
    // Crea una nuova istanza di Pinia per ogni test per isolarli
    setActivePinia(createPinia());
    // Resetta i mock prima di ogni test
    vi.clearAllMocks();
  });

  it('dovrebbe avere uno stato iniziale corretto', () => {
    const store = useRequestLogStore();
    expect(store.logs).toEqual([]);
    expect(store.isLoading).toBe(false);
    expect(store.pagination.offset).toBe(0);
    expect(store.pagination.limit).toBe(25);
    expect(store.sorting.by).toBe('created_at');
    expect(store.sorting.order).toBe('desc');
    expect(store.filters.statusCode).toBe(null);
  });

  describe('Azioni', () => {
    it('fetchRequestLogs dovrebbe recuperare e salvare i log con successo', async () => {
      const store = useRequestLogStore();
      const mockLogs = [{ id: '1', path: '/test', status_code: 200 }];
      requestLogService.getRequestLogs.mockResolvedValue({ data: mockLogs });

      await store.fetchRequestLogs();

      expect(store.isLoading).toBe(false);
      expect(store.logs).toEqual(mockLogs);
      expect(requestLogService.getRequestLogs).toHaveBeenCalledOnce();
    });

    it('fetchRequestLogs dovrebbe gestire gli errori', async () => {
      const store = useRequestLogStore();
      requestLogService.getRequestLogs.mockRejectedValue(new Error('API Error'));

      await store.fetchRequestLogs();

      expect(store.isLoading).toBe(false);
      expect(store.logs).toEqual([]);
    });

    it('clearAllLogs dovrebbe chiamare il servizio e ricaricare i dati', async () => {
      // Mock della funzione `confirm` del browser
      global.confirm = () => true;

      const store = useRequestLogStore();
      requestLogService.clearRequestLogs.mockResolvedValue({ data: { ok: true } });
      requestLogService.getRequestLogs.mockResolvedValue({ data: [] }); // Simula il refetch

      await store.clearAllLogs();

      expect(requestLogService.clearRequestLogs).toHaveBeenCalledOnce();
      expect(requestLogService.getRequestLogs).toHaveBeenCalledOnce(); // Verifica che i dati vengano ricaricati
      expect(store.logs).toEqual([]);
    });

    it('changeSort dovrebbe aggiornare l\'ordinamento e chiamare il servizio API', async () => {
      const store = useRequestLogStore();
      // Mock per evitare che la chiamata fallisca
      requestLogService.getRequestLogs.mockResolvedValue({ data: [] });

      await store.changeSort('path');

      expect(store.sorting.by).toBe('path');
      expect(store.sorting.order).toBe('desc');
      expect(store.pagination.offset).toBe(0);
      // Verifica che il servizio sia stato chiamato, che è l'effetto collaterale corretto
      expect(requestLogService.getRequestLogs).toHaveBeenCalledOnce();
    });
  });
});