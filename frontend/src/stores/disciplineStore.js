import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';

export const useDisciplineStore = defineStore('discipline', () => {
  // --- STATE ---
  const settings = ref(null);
  const manualRules = ref([]);
  const dailyChecklist = ref([]); // For manual rule instances
  const heatmapData = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- GETTERS ---
  const completedRulesCount = computed(() => dailyChecklist.value.filter(item => item.status === 'completed').length);
  const totalRulesCount = computed(() => dailyChecklist.value.length); // This will need adjustment based on automated rules logic

  const dailyScore = computed(() => {
    if (totalRulesCount.value === 0) return 0;
    return Math.round((completedRulesCount.value / totalRulesCount.value) * 100);
  });

  // --- ACTIONS ---

  async function fetchDisciplineSettings() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await apiClient.get('/discipline-settings');
      settings.value = data;
    } catch (err) {
        if (err.response && err.response.status === 404) {
            // If settings don't exist, initialize with default values
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

  async function fetchManualRules() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;
    // This can be part of the initial load, so no separate isLoading
    try {
        const { data } = await apiClient.get('/manual-rules');
        manualRules.value = data;
    } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to fetch manual rules.';
        console.error(error.value);
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


  // This needs to be re-evaluated based on the new logic
  async function fetchDailyChecklist() {
    // ...
  }

  async function updateManualRuleStatus(instanceId, newStatus) {
    // ...
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
    fetchDisciplineSettings,
    saveDisciplineSettings,
    fetchManualRules,
    addManualRule,
    updateManualRule,
    deleteManualRule,
    fetchDailyChecklist,
    updateManualRuleStatus,
    fetchHeatmapData,
  };
});