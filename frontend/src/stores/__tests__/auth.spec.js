import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../auth';
import apiClient, { setAuthToken } from '@/services/api';
import router from '@/router';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mocking apiClient
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  setAuthToken: vi.fn(),
}));

// Mock router
vi.mock('@/router', () => ({
  default: {
    push: vi.fn(),
  },
}));

// Mock all other stores to spy on their $reset method
const mockReset = vi.fn();
vi.mock('../analyticsStore', () => ({ useAnalyticsStore: () => ({ $reset: mockReset }) }));
vi.mock('../dashboardLayout', () => ({ useDashboardLayoutStore: () => ({ $reset: mockReset }) }));
vi.mock('../disciplineStore', () => ({ useDisciplineStore: () => ({ $reset: mockReset }) }));
vi.mock('../filterStore', () => ({ useFilterStore: () => ({ $reset: mockReset }) }));
vi.mock('../imageStore', () => ({ useImageStore: () => ({ $reset: mockReset }) }));
vi.mock('../labelsStore', () => ({ useLabelsStore: () => ({ $reset: mockReset }) }));
vi.mock('../libraryStore', () => ({ useLibraryStore: () => ({ $reset: mockReset }) }));
vi.mock('../loadingStore', () => ({ useLoadingStore: () => ({ $reset: mockReset }) }));
vi.mock('../newsImpactsStore', () => ({ useNewsImpactsStore: () => ({ $reset: mockReset }) }));
vi.mock('../notebookStore', () => ({ useNotebookStore: () => ({ $reset: mockReset }) }));
vi.mock('../playbookStore', () => ({ usePlaybookStore: () => ({ $reset: mockReset }) }));
vi.mock('../tagsStore', () => ({ useTagsStore: () => ({ $reset: mockReset }) }));
vi.mock('../trades', () => ({ useTradesStore: () => ({ $reset: mockReset }) }));
vi.mock('../tradingAccounts', () => ({ useTradingAccountsStore: () => ({ $reset: mockReset }) }));
vi.mock('../tradingDnaStore', () => ({ useTradingDnaStore: () => ({ $reset: mockReset }) }));
vi.mock('../uiStore', () => ({ useUiStore: () => ({ $reset: mockReset }) }));

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  it('register action calls apiClient.post with correct payload', async () => {
    const authStore = useAuthStore();
    const name = 'Test User';
    const email = 'test@example.com';
    const password = 'password123';
    const confirm_password = 'password123';

    // Mock della risposta dell'API
    apiClient.post.mockResolvedValue({ data: { status: 'registered' } });

    await authStore.register(name, email, password, confirm_password);

    expect(apiClient.post).toHaveBeenCalledTimes(1);
    expect(apiClient.post).toHaveBeenCalledWith('/auth/register', {
      name,
      email,
      password,
      confirm_password,
    });
  });

  it('logout action resets all stores, clears localStorage, and redirects', async () => {
    const authStore = useAuthStore();
    const localStorageClearSpy = vi.spyOn(Storage.prototype, 'clear');
    apiClient.post.mockResolvedValue({}); // Mock logout API call

    await authStore.logout();

    // Verifica che l'API di logout sia stata chiamata
    expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');

    // Verifica che tutti gli store mockati siano stati resettati (16 stores)
    expect(mockReset).toHaveBeenCalledTimes(16);

    // Verifica che lo stato interno sia stato pulito manualmente (dato che $reset non è disponibile)
    expect(authStore.user).toBeNull();
    expect(authStore.token).toBeNull();
    expect(authStore.generalAccount).toBeNull();

    // Verifica che il token API sia stato rimosso
    expect(setAuthToken).toHaveBeenCalledWith(null);

    // Verifica che localStorage sia stato pulito
    expect(localStorageClearSpy).toHaveBeenCalledTimes(1);

    // Verifica che l'utente sia stato reindirizzato alla pagina di login
    expect(router.push).toHaveBeenCalledWith('/login');
  });
});