import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTradesStore } from '../trades';
import { useAuthStore } from '../auth';
import apiClient from '../../services/api';

// Mocking the apiClient using vitest
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

// Mocking the auth store
vi.mock('../auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { id: 'mock-user-id-123' },
  })),
}));

describe('useTradesStore', () => {
  beforeEach(() => {
    // Create a new Pinia instance for each test to ensure isolation
    setActivePinia(createPinia());
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  it('fetchTrades action does not send user_id as a parameter', async () => {
    // ARRANGE
    // Mock the API response
    const mockTrades = [{ id: 'trade1', symbol: 'AAPL' }];
    apiClient.get.mockResolvedValue({ data: mockTrades });

    const tradesStore = useTradesStore();

    // ACT
    await tradesStore.fetchTrades();

    // ASSERT
    // Check that apiClient.get was called
    expect(apiClient.get).toHaveBeenCalledOnce();

    // Check the arguments of the call
    const calledWith = apiClient.get.mock.calls[0];
    const url = calledWith[0];
    const config = calledWith[1];

    // 1. Verify the URL is correct
    expect(url).toBe('/api/v1/trades/');

    // 2. Verify that the params object does NOT contain user_id
    expect(config.params).toBeDefined();
    expect(config.params.user_id).toBeUndefined();

    // 3. (Optional) Verify other params are present if needed
    expect(config.params.start_date).toBeDefined();
    expect(config.params.end_date).toBeDefined();
    expect(config.params.user_timezone).toBeDefined();
  });
});
