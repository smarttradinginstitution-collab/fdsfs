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
  }),

  getters: {
    /**
     * Returns all playbooks, useful for selectors or lists.
     * @param {object} state - The current state.
     * @returns {Array} The list of playbooks.
     */
    allPlaybooks(state) {
      return state.playbooks;
    },
  },

  actions: {
    /**
     * Fetches the user's playbooks from the backend, including calculated stats.
     */
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
        // The backend now returns playbooks with a 'stats' object.
        // No special mapping is needed if the frontend can use the structure directly.
        this.playbooks = response.data;
      } catch (err) {
        console.error('Error fetching playbooks:', err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        this.playbooks = []; // Reset on error
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Creates a complete playbook with its rule groups and rules.
     * @param {Array} ruleGroups - The array of rule groups and their rules from the UI.
     * @returns {object} The newly created playbook.
     */
    async createPlaybookWithRules(ruleGroups) {
      if (!this.newPlaybookData) {
        throw new Error("Playbook details from step 1 are missing.");
      }

      this.isLoading = true;
      this.error = null;

      try {
        // 1. Create the playbook
        const playbookResponse = await apiClient.post('/me/playbooks', this.newPlaybookData);
        const newPlaybook = playbookResponse.data;

        // 2. Create the rule groups and their rules
        for (const [index, group] of ruleGroups.entries()) {
          const groupPayload = {
            name_group: group.title,
            playbook_id: newPlaybook.id,
          };
          const groupResponse = await apiClient.post(`/playbooks/${newPlaybook.id}/rule-groups/`, groupPayload);
          const newGroup = groupResponse.data;

          for (const rule of group.rules) {
            const rulePayload = {
              rule: rule.description,
              rules_groups_playbook_id: newGroup.id,
            };
            await apiClient.post(`/rule-groups/${newGroup.id}/rules/`, rulePayload);
          }
        }

        // Add the new playbook to the store and clear the temp data
        this.playbooks.unshift(newPlaybook);
        this.newPlaybookData = null;

        return newPlaybook;

      } catch (err) {
        console.error('Error creating playbook with rules:', err);
        this.error = err.response?.data?.detail || 'A complex error occurred during playbook creation.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Stores the details from the first step of the playbook creation form.
     * @param {object} details - The playbook details from the form.
     */
    setNewPlaybookDetails(details) {
      this.newPlaybookData = details;
    },

    /**
     * Creates a new playbook.
     * @param {object} playbookData - The data for the new playbook.
     * @returns {object} The newly created playbook from the API.
     */
    async createPlaybook(playbookData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/me/playbooks', playbookData);
        const newPlaybook = response.data;
        // Add the new playbook to the start of the local list for immediate UI update
        this.playbooks.unshift(newPlaybook);
        return newPlaybook;
      } catch (err) {
        console.error('Error creating playbook:', err);
        this.error = err.response?.data?.detail || 'Failed to create playbook.';
        throw err; // Re-throw the error so the component can catch it
      } finally {
        this.isLoading = false;
      }
    },
  },
});