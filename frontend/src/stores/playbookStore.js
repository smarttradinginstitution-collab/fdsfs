import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const usePlaybookStore = defineStore('playbooks', {
  state: () => ({
    playbooks: [],
    isLoading: false,
    error: null,
    newPlaybookData: null,
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
        return;
      }
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/me/playbooks');
        this.playbooks = response.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
      } finally {
        this.isLoading = false;
      }
    },

    setNewPlaybookDetails(details) {
      this.newPlaybookData = details;
    },

    async createPlaybookWithRules(ruleGroups) {
      if (!this.newPlaybookData) {
        throw new Error("Playbook details from step 1 are missing.");
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
            name_group: group.title, // Correct field for group name
            playbook_id: newPlaybook.id,
          };
          const groupResponse = await apiClient.post(`/playbooks/${newPlaybook.id}/rule-groups/`, groupPayload);
          const newGroup = groupResponse.data;

          // Step 3: Create the rules for each group
          for (const rule of group.rules) {
            const rulePayload = {
              rule: rule.description, // Correct field for rule text
              rules_groups_playbook_id: newGroup.id,
            };
            await apiClient.post(`/rule-groups/${newGroup.id}/rules/`, rulePayload);
          }
        }

        // Instead of manually adding the playbook, fetch the full, updated list
        // This ensures all data, including calculated stats, is consistent.
        await this.fetchPlaybooks();
        this.newPlaybookData = null;
        return newPlaybook;

      } catch (err) {
        this.error = err.response?.data?.detail || 'An error occurred during playbook creation.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },
  },
});