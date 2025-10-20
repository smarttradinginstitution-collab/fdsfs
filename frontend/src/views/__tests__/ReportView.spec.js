import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import ReportView from '../ReportView.vue';
import { useNotebookStore } from '@/stores/notebookStore';
import { useTradesStore } from '@/stores/trades';
import { useImageStore } from '@/stores/imageStore';

// Mocking vue-router
const mockPush = vi.fn();
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router');
  return {
    ...actual,
    useRoute: () => ({
      params: { id: 'test-trade-id' },
    }),
    useRouter: () => ({
      push: mockPush,
    }),
  };
});

describe('ReportView.vue', () => {
  let notebookStore;

  beforeEach(async () => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
    });

    notebookStore = useNotebookStore(pinia);
    const tradesStore = useTradesStore(pinia);
    const imageStore = useImageStore(pinia);

    // Mock the actions to prevent actual network calls
    tradesStore.fetchTradeById.mockResolvedValue({ id: 'test-trade-id' });
    imageStore.fetchImagesForTrade.mockResolvedValue([]);
    notebookStore.fetchNoteByTradeId.mockResolvedValue(null);

    await mount(ReportView, {
      global: {
        plugins: [pinia],
      },
    });
  });

  it('fetches the trade note when the component is mounted', () => {
    expect(notebookStore.fetchNoteByTradeId).toHaveBeenCalledWith('test-trade-id');
  });
});
