import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';
import { useTradingAccountsStore } from '../tradingAccounts';
import apiClient from '../../services/api';

// Mock dei moduli esterni
vi.mock('../../services/api');
vi.mock('../tradingAccounts');

describe('Trade Store - Getters', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('dovrebbe calcolare correttamente il Net P&L', () => {
    const store = useTradesStore();
    store.trades = [
      { id: 1, pnl: 100 },
      { id: 2, pnl: -50 },
      { id: 3, pnl: 200 }
    ];
    expect(store.netPnl).toBe(250);
  });
});

describe('Trade Store - Actions', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();

    // Simula lo store degli account per restituire un account selezionato
    useTradingAccountsStore.mockReturnValue({
      selectedTradingAccount: { id: 1, initial_balance: 10000 }
    });
  });

  it('fetchTradeById dovrebbe prima caricare tutti i trade se la lista è vuota', async () => {
    const store = useTradesStore();
    const mockTrades = [
      { id: 1, symbol: 'AAPL', p_l: 100, entry_timestamp: '2023-01-01' },
      { id: 2, symbol: 'GOOG', p_l: -50, entry_timestamp: '2023-01-02' }
    ];

    // Mock della risposta API per la lista dei trade
    apiClient.get.mockImplementation(url => {
      if (url.includes('/trades/by-trading-account/')) {
        return Promise.resolve({ data: mockTrades });
      }
      return Promise.reject(new Error(`Chiamata API inaspettata a ${url}`));
    });

    // Stato iniziale: lo store è vuoto
    expect(store.trades.length).toBe(0);

    // Azione: recupera un singolo trade
    await store.fetchTradeById(1);

    // Asserzioni:
    // 1. La chiamata per ottenere TUTTI i trade deve essere stata fatta
    expect(apiClient.get).toHaveBeenCalledWith(
      expect.stringContaining('/trades/by-trading-account/1'),
      expect.any(Object)
    );

    // 2. La lista dei trade ora deve essere popolata
    expect(store.trades.length).toBe(2);

    // 3. Il trade selezionato deve essere quello corretto, preso dalla lista
    expect(store.selectedTrade).not.toBeNull();
    expect(store.selectedTrade.id).toBe(1);
    expect(store.selectedTrade.ticker).toBe('AAPL');

    // 4. La chiamata API per il singolo trade NON deve essere stata fatta
    expect(apiClient.get).not.toHaveBeenCalledWith('/trades/1');
  });
});
