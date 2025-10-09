import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';

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
