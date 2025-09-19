import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';
import apiClient from '../../services/api';

// Mock il modulo apiClient
vi.mock('../../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(), // Mock 'get' per le altre azioni
  },
}));

// Mock lo store di autenticazione per fornire un user ID
vi.mock('../auth', () => ({
  useAuthStore: () => ({
    user: { id: 'test-user-id' },
  }),
}));


describe('Trade Store - Getters', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('dovrebbe calcolare correttamente il Net P&L', () => {
    const store = useTradesStore();
    // Popola lo store con dati di esempio
    store.trades = [
      { pnl: 100 },
      { pnl: -50 },
      { pnl: 200 }
    ];
    // Verifica che il getter calcoli la somma corretta
    expect(store.netPnl).toBe(250);
  });
});

describe('useTradesStore - importTradesCsv Action', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks(); // Resetta i mock prima di ogni test
    // Fornisci un mock di default per le chiamate GET che vengono fatte da fetchAllDataForDashboard
    apiClient.get.mockResolvedValue({ data: [] });
  });

  it('sets isImporting to true during import and false after success', async () => {
    const store = useTradesStore();
    apiClient.post.mockResolvedValue({ data: { summary: {} } });

    const promise = store.importTradesCsv(new File([], 'test.csv'));

    expect(store.isImporting).toBe(true);
    await promise;
    expect(store.isImporting).toBe(false);
  });

  it('sets isImporting to false after failure', async () => {
    const store = useTradesStore();
    apiClient.post.mockRejectedValue(new Error('Network Error'));

    await store.importTradesCsv(new File([], 'test.csv'));

    expect(store.isImporting).toBe(false);
  });

  it('calls apiClient.post with correct FormData and re-fetches data on success', async () => {
    const store = useTradesStore();
    const mockFile = new File(['a,b,c'], 'test.csv', { type: 'text/csv' });
    const mockResponse = { data: { summary: { new_trades_imported: 1 } } };
    apiClient.post.mockResolvedValue(mockResponse);

    // Spy su fetchAllDataForDashboard per verificare che venga chiamata
    const fetchAllSpy = vi.spyOn(store, 'fetchAllDataForDashboard').mockImplementation(async () => {});

    const result = await store.importTradesCsv(mockFile);

    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/v1/trades/import-csv?user_id=test-user-id',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );

    const formData = apiClient.post.mock.calls[0][1];
    expect(formData.get('file')).toBe(mockFile);

    expect(fetchAllSpy).toHaveBeenCalled();
    expect(result).toEqual(mockResponse.data);
  });

  it('returns a formatted error object on API failure', async () => {
    const store = useTradesStore();
    const mockFile = new File(['a,b,c'], 'test.csv');
    const errorResponse = { response: { data: { detail: 'Server Error' } } };
    apiClient.post.mockRejectedValue(errorResponse);

    const result = await store.importTradesCsv(mockFile);

    expect(result.summary.errors_found).toBe(1);
    expect(result.errors[0].error).toBe('Server Error');
  });
});
