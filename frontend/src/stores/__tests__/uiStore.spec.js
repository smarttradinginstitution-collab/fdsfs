import { setActivePinia, createPinia } from 'pinia';
import { useUiStore } from '../uiStore';
import { describe, it, expect, beforeEach } from 'vitest';

describe('useUiStore', () => {
  beforeEach(() => {
    // Crea una nuova istanza Pinia per ogni test per isolarli
    setActivePinia(createPinia());
  });

  it('initializes with import modal closed', () => {
    const store = useUiStore();
    expect(store.isImportModalOpen).toBe(false);
    expect(store.importSummary).toBe(null);
  });

  it('openImportModal sets isImportModalOpen to true', () => {
    const store = useUiStore();
    store.openImportModal();
    expect(store.isImportModalOpen).toBe(true);
  });

  it('closeImportModal sets isImportModalOpen to false and resets summary', () => {
    const store = useUiStore();
    store.openImportModal();
    store.setImportSummary({ success: 1 });

    store.closeImportModal();

    expect(store.isImportModalOpen).toBe(false);
    expect(store.importSummary).toBe(null);
  });

  it('setImportSummary updates the importSummary state', () => {
    const store = useUiStore();
    const summary = {
      new_trades_imported: 10,
      duplicate_trades_skipped: 2,
      errors_found: 1,
    };
    store.setImportSummary(summary);
    expect(store.importSummary).toEqual(summary);
  });
});
