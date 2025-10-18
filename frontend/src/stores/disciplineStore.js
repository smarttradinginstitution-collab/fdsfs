import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useTradingAccountsStore } from './tradingAccounts';
import { useAuthStore } from './auth';

export const useDisciplineStore = defineStore('discipline', () => {
  // --- STATE ---
  const disciplineRules = ref([]);
  const dailyChecklist = ref([]);
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

  async function createDisciplineRule(ruleData) {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await apiClient.post('/discipline/rules', ruleData);
      disciplineRules.value.push(data);
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create rule.';
      console.error(error.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateDisciplineRule(ruleId, ruleData) {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await apiClient.put(`/discipline/rules/${ruleId}`, ruleData);
      const index = disciplineRules.value.findIndex(r => r.id === ruleId);
      if (index !== -1) {
        disciplineRules.value[index] = data;
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update rule.';
      console.error(error.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteDisciplineRule(ruleId) {
    isLoading.value = true;
    error.value = null;
    try {
      await apiClient.delete(`/discipline/rules/${ruleId}`);
      disciplineRules.value = disciplineRules.value.filter(r => r.id !== ruleId);
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete rule.';
      console.error(error.value);
      throw err;
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

  return {
    disciplineRules,
    dailyChecklist,
    isLoading,
    error,
    manualRules,
    automatedRules,
    completedRulesCount,
    totalRulesCount,
    dailyScore,
    fetchDisciplineRules,
    fetchDailyChecklist,
    createDisciplineRule,
    updateDisciplineRule,
    deleteDisciplineRule,
    updateManualRuleStatus,
  };
});