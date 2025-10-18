import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useTradingAccountsStore } from './tradingAccounts';
import { useAuthStore } from './auth';

export const useDisciplineStore = defineStore('discipline', () => {
  // --- STATE ---
  const disciplineRules = ref([]);
  const dailyChecklist = ref([]);
  const heatmapData = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- GETTERS ---
  const manualRules = computed(() => dailyChecklist.value.filter(item => item.rule_type === 'MANUAL'));
  const automatedRules = computed(() => dailyChecklist.value.filter(item => item.rule_type === 'AUTOMATED'));

  const completedRulesCount = computed(() => dailyChecklist.value.filter(item => item.status === 'completed').length);
  const totalRulesCount = computed(() => dailyChecklist.value.length);

  const dailyScore = computed(() => {
    if (totalRulesCount.value === 0) return 0;
    return Math.round((completedRulesCount.value / totalRulesCount.value) * 100);
  });

  // --- ACTIONS ---

  async function fetchDisciplineRules() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await apiClient.get('/discipline/rules');
      disciplineRules.value = data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch discipline rules.';
      console.error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchDailyChecklist() {
    const authStore = useAuthStore();
    const tradingAccountsStore = useTradingAccountsStore();
    if (!authStore.isAuthenticated || !tradingAccountsStore.selectedTradingAccount) {
      dailyChecklist.value = [];
      return;
    }

    isLoading.value = true;
    error.value = null;
    try {
      const tradingAccountId = tradingAccountsStore.selectedTradingAccount.id;
      const { data } = await apiClient.get(`/discipline/daily-checklist?trading_account_id=${tradingAccountId}`);
      dailyChecklist.value = data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch daily checklist.';
      console.error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function bulkUpdateDisciplineRules(rules) {
    const tradingAccountsStore = useTradingAccountsStore();
    if (!tradingAccountsStore.selectedTradingAccount) {
      error.value = "No trading account selected.";
      return;
    }

    isLoading.value = true;
    error.value = null;
    try {
      const tradingAccountId = tradingAccountsStore.selectedTradingAccount.id;
      const payload = { rules: rules };
      const { data } = await apiClient.post(`/discipline/rules/bulk-update?trading_account_id=${tradingAccountId}`, payload);

      // Replace local rules with the server's response
      disciplineRules.value = data;

      // Refresh the daily checklist to reflect changes
      await fetchDailyChecklist();

    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update rules.';
      console.error(error.value);
      throw err; // Re-throw to be caught in the component
    } finally {
      isLoading.value = false;
    }
  }

  async function updateManualRuleStatus(instanceId, newStatus) {
    const item = dailyChecklist.value.find(i => i.id === instanceId);
    if (!item || item.rule_type !== 'MANUAL') return;

    const originalStatus = item.status;
    item.status = newStatus; // Optimistic update

    try {
      await apiClient.put(`/discipline/daily-checklist/${instanceId}`, { status: newStatus });
    } catch (err) {
      item.status = originalStatus; // Revert on error
      error.value = err.response?.data?.detail || 'Failed to update rule status.';
      console.error(error.value);
    }
  }

  async function fetchHeatmapData(year, month) {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    // No need for isLoading here, can run in background
    error.value = null;
    try {
      const { data } = await apiClient.get(`/discipline/heatmap?year=${year}&month=${month}`);
      heatmapData.value = data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch heatmap data.';
      console.error(error.value);
    }
  }

  return {
    disciplineRules,
    dailyChecklist,
    heatmapData,
    isLoading,
    error,
    manualRules,
    automatedRules,
    completedRulesCount,
    totalRulesCount,
    dailyScore,
    fetchDisciplineRules,
    fetchDailyChecklist,
    bulkUpdateDisciplineRules,
    updateManualRuleStatus,
    fetchHeatmapData,
  };
});