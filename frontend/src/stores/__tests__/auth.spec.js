import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../auth';
import apiClient from '@/services/api';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mocking apiClient
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
  },
}));

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
});