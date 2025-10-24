import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';
import apiClient from '../../services/api';

vi.mock('../../services/api');

describe('Trade Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('dovrebbe calcolare correttamente il Net P&L', () => {
    const store = useTradesStore();
    store.trades = [
      { pnl: 100 },
      { pnl: -50 },
      { pnl: 200 }
    ];
    expect(store.netPnl).toBe(250);
  });

  it('mantains calculated fields after updating a trade', async () => {
    const store = useTradesStore();
    const tradeId = 'test-trade-id';

    const initialTradeData = {
      id: tradeId,
      p_l: 150,
      mfe: 200,
      mae: -50,
    };

    // 1. Mock the initial fetch
    apiClient.get.mockResolvedValue({ data: initialTradeData });
    await store.fetchTradeWithAllData(tradeId);

    // Verify initial state
    expect(store.selectedTrade).toBeDefined();
    expect(store.selectedTrade.id).toBe(tradeId);
    expect(store.selectedTrade.mfe).toBe(200);

    // 2. Mock the update and the subsequent re-fetch
    const updatedTradeData = {
      id: tradeId,
      p_l: 160,
      mfe: 210,
      mae: -40,
    };
    apiClient.put.mockResolvedValue({ data: { id: tradeId, p_l: 160 } }); // Partial response
    apiClient.get.mockResolvedValue({ data: updatedTradeData }); // Full response for re-fetch

    // 3. Trigger the update action
    await store.updateTrade(tradeId, { p_l: 160 });

    // 4. Assert the final state
    expect(apiClient.put).toHaveBeenCalledWith(`/trades/${tradeId}`, { p_l: 160 });
    expect(apiClient.get).toHaveBeenCalledWith(`/trades/with-data/${tradeId}`);
    expect(store.selectedTrade).toBeDefined();
    expect(store.selectedTrade.mfe).toBe(210); // Check that the calculated field is present and updated
    expect(store.selectedTrade.p_l).toBe(160);
  });
});
