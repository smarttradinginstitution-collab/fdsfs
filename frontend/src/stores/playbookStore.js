import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const usePlaybookStore = defineStore('playbooks', {
  state: () => ({
    playbooks: [],
    isLoading: false,
    error: null,
    // Holds the data from Step 1 of the creation process
    newPlaybookData: null,
    // Analytics for the detail page
    currentPlaybookAnalytics: null,
    isAnalyticsLoading: false,

    // State for the Playbook Rules tab
    ruleGroups: [],
    isRuleGroupsLoading: false,
    ruleGroupsError: null,
  }),

  getters: {
    allPlaybooks(state) {
      return state.playbooks;
    },
  },

  actions: {
    async fetchPlaybooks() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.log("User not authenticated. Skipping playbook fetch.");
        return;
      }
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/me/playbooks');
        this.playbooks = response.data;
      } catch (err) {
        console.error('Error fetching playbooks:', err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        this.playbooks = [];
      } finally {
        this.isLoading = false;
      }
    },

    setNewPlaybookDetails(details) {
      this.newPlaybookData = details;
    },

    async createPlaybookWithRules(ruleGroups) {
      if (!this.newPlaybookData) {
        throw new Error("Playbook details from Step 1 are missing.");
      }

      this.isLoading = true;
      this.error = null;
      try {
        // Step 1: Create the playbook
        const playbookResponse = await apiClient.post('/me/playbooks', this.newPlaybookData);
        const newPlaybook = playbookResponse.data;

        // Step 2: Create the rule groups
        for (const group of ruleGroups) {
          const groupPayload = {
            name_group: group.title, // Correct field name for the group title
            playbook_id: newPlaybook.id,
          };
          const groupResponse = await apiClient.post(`/playbooks/${newPlaybook.id}/rule-groups/`, groupPayload);
          const newGroup = groupResponse.data;

          // Step 3: Create the rules for each group
          for (const rule of group.rules) {
            const rulePayload = {
              rule: rule.description, // Correct field name for the rule text
              rules_groups_playbook_id: newGroup.id,
            };
            await apiClient.post(`/rule-groups/${newGroup.id}/rules/`, rulePayload);
          }
        }

        // Fetch the updated list to ensure data consistency
        await this.fetchPlaybooks();
        this.newPlaybookData = null;
        return newPlaybook;

      } catch (err) {
        console.error('Error creating playbook with rules:', err);
        this.error = err.response?.data?.detail || 'An error occurred during playbook creation.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchPlaybookAnalytics(playbookId) {
      this.isAnalyticsLoading = true;
      this.error = null;
      this.currentPlaybookAnalytics = null; // Reset before fetching
      try {
        const response = await apiClient.get(`/playbooks/${playbookId}/analytics`);
        this.currentPlaybookAnalytics = response.data;
      } catch (err) {
        console.error(`Error fetching analytics for playbook ${playbookId}:`, err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred fetching playbook analytics.';
      } finally {
        this.isAnalyticsLoading = false;
      }
    },

    async fetchRuleGroups(playbookId) {
      this.isRuleGroupsLoading = true;
      this.ruleGroupsError = null;
      try {
        const response = await apiClient.get(`/playbooks/${playbookId}/rule-groups/`);
        this.ruleGroups = response.data;
      } catch (err) {
        console.error(`Error fetching rule groups for playbook ${playbookId}:`, err);
        this.ruleGroupsError = err.response?.data?.detail || 'An unexpected error occurred fetching rule groups.';
        this.ruleGroups = []; // Reset on error
      } finally {
        this.isRuleGroupsLoading = false;
      }
    },

    async reorderRuleGroups(playbookId, group_ids) {
      try {
        await apiClient.put(`/playbooks/${playbookId}/rule-groups/reorder`, { group_ids });
        // No need to refetch, optimistic update is handled by vuedraggable's v-model.
        // A full refetch could cause a jarring UI update.
      } catch (err) {
        console.error('Error reordering rule groups:', err);
        // Optionally, dispatch an error to the UI and refetch to revert the change
        this.ruleGroupsError = err.response?.data?.detail || 'Failed to save new group order.';
        this.fetchRuleGroups(playbookId); // Revert UI on failure
      }
    },

    async reorderRules({ playbookId, groupId, rule_ids }) {
      try {
        await apiClient.put(`/rule-groups/${groupId}/rules/reorder`, { rule_ids });
      } catch (err) {
        console.error('Error reordering rules:', err);
        this.ruleGroupsError = err.response?.data?.detail || 'Failed to save new rule order.';
        // Re-fetch the entire group structure to ensure consistency on failure
        this.fetchRuleGroups(playbookId);
      }
    },
  },
});