import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';
import { useTradingAccountsStore } from '../tradingAccounts';
import apiClient from '../../services/api';

// Mock del modulo apiClient
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    put: vi.fn(),
  },
}));

describe('Trade Store', () => {
  beforeEach(() => {
    // Crea una nuova istanza di Pinia per ogni test per isolare gli stati
    setActivePinia(createPinia());
    // Resetta i mock prima di ogni test
    vi.clearAllMocks();
  });

  describe('Getters', () => {
    it('dovrebbe calcolare correttamente il Net P&L', () => {
      const store = useTradesStore();
      store.trades = [{ pnl: 100 }, { pnl: -50 }, { pnl: 200 }];
      expect(store.netPnl).toBe(250);
    });

    it('getPreviousTradeId e getNextTradeId dovrebbero funzionare correttamente', () => {
        const store = useTradesStore();
        store.trades = [
            { id: '1', date: '2023-01-01' },
            { id: '2', date: '2023-01-02' },
            { id: '3', date: '2023-01-03' },
        ];
        store.selectedTrade = { id: '2' };

        expect(store.getPreviousTradeId).toBe('1');
        expect(store.getNextTradeId).toBe('3');
    });

    it('allDashboardStats dovrebbe restituire statistiche vuote di default', () => {
        const store = useTradesStore();
        const stats = store.allDashboardStats;
        expect(stats.netPnl.value).toBe('$0.00');
        expect(stats.trades.value).toBe('0');
    });
  });

  describe('Actions', () => {
    it('fetchTrades dovrebbe recuperare e mappare i trade se un account è selezionato', async () => {
      const tradesStore = useTradesStore();
      const accountsStore = useTradingAccountsStore();

      // Simula un account di trading selezionato
      accountsStore.selectedTradingAccount = { id: 'account-1' };

      const mockTrades = [{ id: 'trade-1', p_l: 150, direction: 'LONG' }];
      apiClient.get.mockResolvedValue({ data: mockTrades });

      await tradesStore.fetchTrades();

      expect(apiClient.get).toHaveBeenCalledWith('/trades/by-trading-account/account-1', expect.any(Object));
      expect(tradesStore.trades.length).toBe(1);
      expect(tradesStore.trades[0].id).toBe('trade-1');
      expect(tradesStore.trades[0].pnl).toBe(150);
      expect(tradesStore.isLoading).toBe(false);
    });

    it('fetchTrades non dovrebbe fare nulla se nessun account è selezionato', async () => {
      const tradesStore = useTradesStore();
      const accountsStore = useTradingAccountsStore();

      accountsStore.selectedTradingAccount = null;

      await tradesStore.fetchTrades();

      expect(apiClient.get).not.toHaveBeenCalled();
      expect(tradesStore.trades.length).toBe(0);
      expect(tradesStore.isLoading).toBe(false);
    });

    it('addTrade dovrebbe inviare i dati corretti e aggiornare lo stato', async () => {
      const tradesStore = useTradesStore();
      const accountsStore = useTradingAccountsStore();
      accountsStore.selectedTradingAccount = { id: 'account-1' };

      const newTradeData = { pnl: 200, symbol_snapshot: 'AAPL' };
      const responseData = { id: 'new-trade', ...newTradeData };
      apiClient.post.mockResolvedValue({ data: responseData });
      // Mock per le chiamate di aggiornamento delle statistiche
      apiClient.get.mockResolvedValue({ data: {} });

      await tradesStore.addTrade(newTradeData);

      expect(apiClient.post).toHaveBeenCalledWith('/trades/', expect.objectContaining({
        trading_account_id: 'account-1',
        p_l: 200,
        symbol_snapshot: 'AAPL',
      }));
      expect(tradesStore.trades[0].id).toBe('new-trade');
    });

    it('deleteTrade dovrebbe chiamare l\'API e rimuovere il trade dallo stato', async () => {
        const tradesStore = useTradesStore();
        tradesStore.trades = [{ id: 'trade-to-delete', pnl: 100 }];

        apiClient.delete.mockResolvedValue({});
        // Mock per le chiamate di aggiornamento dei dati
        apiClient.get.mockResolvedValue({ data: { stats: {} } });

        await tradesStore.deleteTrade('trade-to-delete');

        expect(apiClient.delete).toHaveBeenCalledWith('/trades/trade-to-delete');
        expect(tradesStore.trades.length).toBe(0);
    });

    it('fetchAllDataForDashboard non dovrebbe eseguire fetch duplicati se è già in corso', async () => {
        const tradesStore = useTradesStore();
        tradesStore.isLoading = true; // Simula un caricamento in corso

        await tradesStore.fetchAllDataForDashboard();

        // Dato che isLoading è true, nessuna chiamata API dovrebbe partire
        expect(apiClient.get).not.toHaveBeenCalled();

        tradesStore.isLoading = false; // Resetta per altri test
    });
  });
});
