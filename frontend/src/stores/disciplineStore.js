import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';
import { useTradingAccountsStore } from './tradingAccounts';

export const useDisciplineStore = defineStore('discipline', () => {
  // --- STATE ---
  const settings = ref(null);
  const manualRules = ref([]);
  const dailyChecklist = ref({ manual_rules: [], automated_rules: [] });
  const heatmapData = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- GETTERS ---
  const completedRulesCount = computed(() => {
    const manualCompleted = dailyChecklist.value.manual_rules.filter(item => item.status === 'completed').length;
    const automatedCompleted = dailyChecklist.value.automated_rules.filter(item => item.status === 'completed').length;
    return manualCompleted + automatedCompleted;
  });

  const totalRulesCount = computed(() => {
    return (dailyChecklist.value.manual_rules?.length || 0) + (dailyChecklist.value.automated_rules?.length || 0);
  });

  const dailyScore = computed(() => {
    if (totalRulesCount.value === 0) return 0;
    return Math.round((completedRulesCount.value / totalRulesCount.value) * 100);
  });

  const allRules = ref([]);

  // --- ACTIONS ---

  async function fetchAllRules() {
    const authStore = useAuthStore();
    const tradingAccountsStore = useTradingAccountsStore();
    if (!authStore.isAuthenticated || !tradingAccountsStore.selectedTradingAccount) {
      allRules.value = [];
      return;
    }

    const tradingAccountId = tradingAccountsStore.selectedTradingAccount.id;
    const { data } = await apiClient.get(`/rules-with-statistics?trading_account_id=${tradingAccountId}`);
    allRules.value = data;

    // Extract settings and manual rules from the allRules response
    const automatedRulesSettings = data.find(rule => !rule.isManual)?.settings;
    if (automatedRulesSettings) {
        settings.value = automatedRulesSettings;
    } else {
        // If no automated rules, fetch settings separately or set defaults
        await fetchDisciplineSettings();
    }
    manualRules.value = data.filter(rule => rule.isManual);
  }

  // This function can be kept for cases where only settings are needed,
  // or be removed if fetchAllRules is always the entry point.
  async function fetchDisciplineSettings() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) return;

      try {
          const { data } = await apiClient.get('/discipline-settings');
          settings.value = data;
      } catch (err) {
          if (err.response && err.response.status === 404) {
              settings.value = {
                  trading_days: [1, 2, 3, 4, 5],
                  start_day_by: null,
                  link_trades_to_playbook_threshold: 100,
                  trade_has_stop_loss_threshold: 100,
                  max_loss_per_trade_type: '$',
                  max_loss_per_trade_value: 0,
                  max_loss_per_day: 0,
              };
          } else {
              error.value = err.response?.data?.detail || 'Failed to fetch discipline settings.';
              console.error(error.value);
          }
      }
  }

  // New action to orchestrate initial data loading
  async function initializeStore() {
    isLoading.value = true;
    error.value = null;
    try {
      await Promise.all([
        fetchAllRules(),
        fetchDailyChecklist(),
      ]);
    } catch (err) {
      // Error is already set by the individual functions
      console.error("Failed to initialize discipline store:", err);
    } finally {
      isLoading.value = false;
    }
  }

  async function saveDisciplineSettings(newSettings) {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await apiClient.post('/discipline-settings', newSettings);
      settings.value = data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to save settings.';
      console.error(error.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function addManualRule(ruleData) {
      isLoading.value = true;
      try {
          const { data } = await apiClient.post('/manual-rules', ruleData);
          manualRules.value.push(data);
      } catch (err) {
          error.value = err.response?.data?.detail || 'Failed to add manual rule.';
          console.error(error.value);
          throw err;
      } finally {
          isLoading.value = false;
      }
  }

  async function updateManualRule(ruleId, ruleData) {
      isLoading.value = true;
      try {
          const { data } = await apiClient.put(`/manual-rules/${ruleId}`, ruleData);
          const index = manualRules.value.findIndex(r => r.id === ruleId);
          if (index !== -1) {
              manualRules.value[index] = data;
          }
      } catch (err) {
          error.value = err.response?.data?.detail || 'Failed to update manual rule.';
          console.error(error.value);
          throw err;
      } finally {
          isLoading.value = false;
      }
  }

  async function deleteManualRule(ruleId) {
      isLoading.value = true;
      try {
          await apiClient.delete(`/manual-rules/${ruleId}`);
          manualRules.value = manualRules.value.filter(r => r.id !== ruleId);
      } catch (err) {
          error.value = err.response?.data?.detail || 'Failed to delete manual rule.';
          console.error(error.value);
          throw err;
      } finally {
          isLoading.value = false;
      }
  }


  async function fetchDailyChecklist() {
    const authStore = useAuthStore();
    const tradingAccountsStore = useTradingAccountsStore();
    if (!authStore.isAuthenticated || !tradingAccountsStore.selectedTradingAccount) {
      dailyChecklist.value = { manual_rules: [], automated_rules: [] };
      return;
    }

    isLoading.value = true;
    error.value = null;
    try {
      const tradingAccountId = tradingAccountsStore.selectedTradingAccount.id;
      const { data } = await apiClient.get(`/daily-checklist?trading_account_id=${tradingAccountId}`);
      dailyChecklist.value = data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch daily checklist.';
      console.error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function updateManualRuleStatus(instanceId, newStatus) {
    const rule = dailyChecklist.value.manual_rules.find(r => r.id === instanceId);
    if (!rule) return;

    const originalStatus = rule.status;
    rule.status = newStatus; // Optimistic update

    try {
      await apiClient.put(`/daily-checklist/${instanceId}`, { status: newStatus });
      // After a successful update, refresh the rules table to show new stats
      await fetchAllRules();
    } catch (err) {
      rule.status = originalStatus; // Rollback on error
      error.value = err.response?.data?.detail || 'Failed to update rule status.';
      console.error(error.value);
    }
  }

  async function fetchHeatmapData(year, month) {
    // ...
  }

  return {
    settings,
    manualRules,
    dailyChecklist,
    heatmapData,
    isLoading,
    error,
    completedRulesCount,
    totalRulesCount,
    dailyScore,
    allRules,
    fetchAllRules,
    fetchDisciplineSettings,
    saveDisciplineSettings,
    addManualRule,
    updateManualRule,
    deleteManualRule,
    fetchDailyChecklist,
    updateManualRuleStatus,
    fetchHeatmapData,
    initializeStore,
  };
});