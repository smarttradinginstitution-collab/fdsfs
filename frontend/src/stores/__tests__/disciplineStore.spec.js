import { setActivePinia, createPinia } from 'pinia';
import { useDisciplineStore } from '../disciplineStore';
import apiClient from '@/services/api';
import { useAuthStore } from '../auth';
import { useTradingAccountsStore } from '../tradingAccounts';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the external dependencies
vi.mock('@/services/api');
vi.mock('../auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: true,
  }),
}));
vi.mock('../tradingAccounts', () => ({
    useTradingAccountsStore: vi.fn(() => ({
        selectedTradingAccount: { id: 'test-account-id' },
    })),
}));

describe('Discipline Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('fetches discipline settings successfully', async () => {
    const disciplineStore = useDisciplineStore();
    const mockSettings = { id: '1', trading_days: [1, 2, 3] };
    apiClient.get.mockResolvedValue({ data: mockSettings });

    await disciplineStore.fetchDisciplineSettings();

    expect(disciplineStore.settings).toEqual(mockSettings);
    expect(apiClient.get).toHaveBeenCalledWith('/discipline-settings');
  });

  it('initializes default settings on 404 error', async () => {
    const disciplineStore = useDisciplineStore();
    apiClient.get.mockRejectedValue({ response: { status: 404 } });

    await disciplineStore.fetchDisciplineSettings();

    expect(disciplineStore.settings).toBeDefined();
    expect(disciplineStore.settings.trade_has_stop_loss_threshold).toBe(100);
  });

  it('saves discipline settings', async () => {
    const disciplineStore = useDisciplineStore();
    const newSettings = { trading_days: [1, 2, 3, 4, 5] };
    const savedSettings = { id: '1', ...newSettings };
    apiClient.post.mockResolvedValue({ data: savedSettings });

    await disciplineStore.saveDisciplineSettings(newSettings);

    expect(disciplineStore.settings).toEqual(savedSettings);
    expect(apiClient.post).toHaveBeenCalledWith('/discipline-settings', newSettings);
  });

  it('fetches all rules with statistics', async () => {
    const disciplineStore = useDisciplineStore();
    const mockRules = [{ id: '1', name: 'Rule 1', follow_rate: 100, avg_performance: 'N/A' }];
    apiClient.get.mockResolvedValue({ data: mockRules });

    await disciplineStore.fetchAllRules();

    expect(disciplineStore.allRules).toEqual(mockRules);
    expect(apiClient.get).toHaveBeenCalledWith('/rules-with-statistics?trading_account_id=test-account-id');
  });

  it('adds a manual rule', async () => {
    const disciplineStore = useDisciplineStore();
    const newRule = { name: 'New Rule', frequency: [1, 2, 3] };
    const createdRule = { id: '2', ...newRule };
    apiClient.post.mockResolvedValue({ data: createdRule });

    await disciplineStore.addManualRule(newRule);

    expect(disciplineStore.manualRules).toContainEqual(createdRule);
    expect(apiClient.post).toHaveBeenCalledWith('/manual-rules', newRule);
  });

  it('deletes a manual rule', async () => {
    const disciplineStore = useDisciplineStore();
    const ruleId = '1';
    disciplineStore.manualRules = [{ id: ruleId, name: 'Rule to delete' }];
    apiClient.delete.mockResolvedValue({});

    await disciplineStore.deleteManualRule(ruleId);

    expect(disciplineStore.manualRules).not.toContain(expect.objectContaining({ id: ruleId }));
    expect(apiClient.delete).toHaveBeenCalledWith(`/manual-rules/${ruleId}`);
  });
});