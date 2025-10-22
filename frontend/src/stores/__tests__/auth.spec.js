import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../auth';
import apiClient, { setAuthToken } from '@/services/api';
import router from '@/router';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mocking apiClient and router
vi.mock('@/services/api', () => ({
  default: { post: vi.fn(), get: vi.fn() },
  setAuthToken: vi.fn(),
}));
vi.mock('@/router', () => ({ default: { push: vi.fn() } }));

// Mocks for store reset methods
const mockResetState = vi.fn(); // For setup stores
const mockDollarReset = vi.fn(); // For options stores

// Mock all stores to spy on their reset methods
vi.mock('../analyticsStore', () => ({ useAnalyticsStore: () => ({ resetState: mockResetState }) }));
vi.mock('../disciplineStore', () => ({ useDisciplineStore: () => ({ resetState: mockResetState }) }));
vi.mock('../filterStore', () => ({ useFilterStore: () => ({ resetState: mockResetState }) }));
vi.mock('../imageStore', () => ({ useImageStore: () => ({ resetState: mockResetState }) }));
vi.mock('../labelsStore', () => ({ useLabelsStore: () => ({ resetState: mockResetState }) }));
vi.mock('../libraryStore', () => ({ useLibraryStore: () => ({ resetState: mockResetState }) }));
vi.mock('../loadingStore', () => ({ useLoadingStore: () => ({ resetState: mockResetState }) }));
vi.mock('../newsImpactsStore', () => ({ useNewsImpactsStore: () => ({ resetState: mockResetState }) }));
vi.mock('../tagsStore', () => ({ useTagsStore: () => ({ resetState: mockResetState }) }));
vi.mock('../tradingAccounts', () => ({ useTradingAccountsStore: () => ({ resetState: mockResetState }) }));
vi.mock('../tradingDnaStore', () => ({ useTradingDnaStore: () => ({ resetState: mockResetState }) }));
vi.mock('../uiStore', () => ({ useUiStore: () => ({ resetState: mockResetState }) }));

vi.mock('../dashboardLayout', () => ({ useDashboardLayoutStore: () => ({ $reset: mockDollarReset }) }));
vi.mock('../notebookStore', () => ({ useNotebookStore: () => ({ $reset: mockDollarReset }) }));
vi.mock('../playbookStore', () => ({ usePlaybookStore: () => ({ $reset: mockDollarReset }) }));
vi.mock('../trades', () => ({ useTradesStore: () => ({ $reset: mockDollarReset }) }));


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

  it('logout action calls the correct reset method on all stores', async () => {
    const authStore = useAuthStore();
    const localStorageClearSpy = vi.spyOn(Storage.prototype, 'clear');
    apiClient.post.mockResolvedValue({});

    await authStore.logout();

    // Verifica che l'API di logout sia stata chiamata
    expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');

    // Verifica che i metodi di reset corretti siano stati chiamati
    expect(mockResetState).toHaveBeenCalledTimes(12); // 12 setup stores
    expect(mockDollarReset).toHaveBeenCalledTimes(4); // 4 options stores

    // Verifica che lo stato interno sia stato pulito manualmente
    expect(authStore.user).toBeNull();
    expect(authStore.token).toBeNull();
    expect(authStore.generalAccount).toBeNull();

    // Verifica che il token API e localStorage siano stati puliti
    expect(setAuthToken).toHaveBeenCalledWith(null);
    expect(localStorageClearSpy).toHaveBeenCalledTimes(1);

    // Verifica il reindirizzamento
    expect(router.push).toHaveBeenCalledWith('/login');
  });
});