import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const usePlaybookStore = defineStore('playbooks', {
  state: () => ({
    playbooks: [],
    isLoading: false,
    error: null,
    // Analytics for the detail page
    currentPlaybookAnalytics: null,
    isAnalyticsLoading: false,
  }),

  getters: {
    allPlaybooks(state) {
      return state.playbooks;
    },
    getPlaybookById: (state) => (id) => {
      return state.playbooks.find((playbook) => playbook.id === id);
    },
  },

  actions: {
    async fetchPlaybookDetails(playbookId) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get(`/playbooks/${playbookId}`);
        // We can update the playbook in the list if it's already there, or add it.
        const index = this.playbooks.findIndex(p => p.id === playbookId);
        if (index !== -1) {
          this.playbooks[index] = response.data;
        } else {
          this.playbooks.push(response.data);
        }
        return response.data;
      } catch (err) {
        console.error(`Error fetching details for playbook ${playbookId}:`, err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        throw err; // Re-throw to let the component handle it (e.g., redirect)
      } finally {
        this.isLoading = false;
      }
    },

    async createBlockForPlaybook({ playbookId, block_type, title, content, order }) {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await apiClient.post(`/playbooks/${playbookId}/blocks`, {
                block_type: block_type,
                title: title,
                content: content,
                order: order,
            });
            const newBlock = response.data;
            // Find the playbook and add the new block to its blocks array
            const playbook = this.playbooks.find(p => p.id === playbookId);
            if (playbook) {
                if (!playbook.blocks) {
                    playbook.blocks = [];
                }
                playbook.blocks.push(newBlock);
            }
            return newBlock;
        } catch (err) {
            console.error('Error creating playbook block:', err);
            this.error = err.response?.data?.detail || 'Failed to create a new block.';
            throw err;
        } finally {
            this.isLoading = false;
        }
    },

    async updateBlock(playbookId, blockId, blockData) {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await apiClient.put(`/playbooks/${playbookId}/blocks/${blockId}`, blockData);
            const updatedBlock = response.data;

            const playbook = this.playbooks.find(p => p.id === playbookId);
            if (playbook && playbook.blocks) {
                const index = playbook.blocks.findIndex(b => b.id === blockId);
                if (index !== -1) {
                    playbook.blocks[index] = updatedBlock;
                }
            }
        } catch (err) {
            console.error('Error updating playbook block:', err);
            this.error = err.response?.data?.detail || 'Failed to update block.';
            throw err;
        } finally {
            this.isLoading = false;
        }
    },

    async deleteBlock(playbookId, blockId) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.delete(`/playbooks/${playbookId}/blocks/${blockId}`);

            const playbook = this.playbooks.find(p => p.id === playbookId);
            if (playbook && playbook.blocks) {
                playbook.blocks = playbook.blocks.filter(b => b.id !== blockId);
            }
        } catch (err) {
            console.error('Error deleting playbook block:', err);
            this.error = err.response?.data?.detail || 'Failed to delete block.';
            throw err;
        } finally {
            this.isLoading = false;
        }
    },

    async updatePlaybook(playbookId, playbookData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/playbooks/${playbookId}`, playbookData);
        const updatedPlaybook = response.data;
        const index = this.playbooks.findIndex(p => p.id === playbookId);
        if (index !== -1) {
          this.playbooks[index] = { ...this.playbooks[index], ...updatedPlaybook };
        }
      } catch (err) {
        console.error(`Error updating playbook ${playbookId}:`, err);
        this.error = err.response?.data?.detail || 'An error occurred during playbook update.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deletePlaybook(playbookId) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.delete(`/playbooks/${playbookId}`);
        // Remove the playbook from the local state
        this.playbooks = this.playbooks.filter(p => p.id !== playbookId);
      } catch (err) {
        console.error(`Error deleting playbook ${playbookId}:`, err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred while deleting the playbook.';
        // Re-throw the error so the component knows the operation failed
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

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

    async createPlaybook(playbookData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/me/playbooks', playbookData);
        const newPlaybook = response.data;
        this.playbooks.push(newPlaybook);
        return newPlaybook;
      } catch (err) {
        console.error('Error creating playbook:', err);
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

    async updatePlaybookBlocks({ playbookId, blocks }) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/playbooks/${playbookId}/blocks`, blocks);
        const updatedBlocks = response.data;
        const playbook = this.playbooks.find(p => p.id === playbookId);
        if (playbook) {
          playbook.blocks = updatedBlocks;
        }
      } catch (err) {
        console.error('Error updating playbook blocks:', err);
        this.error = err.response?.data?.detail || 'Failed to update playbook blocks.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async updatePlaybookConditions({ playbookId, conditions }) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/playbooks/${playbookId}/conditions`, conditions);
        const updatedConditions = response.data;
        const playbook = this.playbooks.find(p => p.id === playbookId);
        if (playbook) {
          playbook.conditions = updatedConditions;
        }
      } catch (err) {
        console.error('Error updating playbook conditions:', err);
        this.error = err.response?.data?.detail || 'Failed to update playbook conditions.';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },
  },
});