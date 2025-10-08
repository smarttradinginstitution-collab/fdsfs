import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tags: [],
    tagGroups: [],
    isLoading: false,
    isSaving: false,
    error: null,
  }),

  getters: {
    groupedTags(state) {
      if (!state.tagGroups.length || !state.tags.length) {
        return [];
      }
      return state.tagGroups.map(group => ({
        ...group,
        tags: state.tags.filter(tag => tag.tags_group_id === group.id),
      }));
    },
  },

  actions: {
    async fetchTags() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.log("User not authenticated. Skipping tags fetch.");
        return;
      }
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/me/tags');
        this.tags = response.data;
      } catch (err) {
        console.error('Error fetching tags:', err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        this.tags = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTagGroups() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.log("User not authenticated. Skipping tag groups fetch.");
        return;
      }
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/tags-groups');
        this.tagGroups = response.data;
      } catch (err) {
        console.error('Error fetching tag groups:', err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        this.tagGroups = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchAllTagsData() {
        this.isLoading = true;
        this.error = null;
        try {
            await Promise.all([this.fetchTags(), this.fetchTagGroups()]);
        } catch (err) {
            console.error('Error fetching all tags data:', err);
            this.error = 'An error occurred while fetching tags information.';
        } finally {
            this.isLoading = false;
        }
    },

    // --- GROUP ACTIONS ---
    async createTagGroup(groupData) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.post('/tags-groups', groupData);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Group created successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to create group.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    },

    async updateTagGroup(groupId, groupData) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.put(`/tags-groups/${groupId}`, groupData);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Group updated successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to update group.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    },

    async deleteTagGroup(groupId) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.delete(`/tags-groups/${groupId}`);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Group deleted successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to delete group.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    },

    // --- TAG ACTIONS ---
    async createTag(tagData) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.post('/me/tags', tagData);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Tag created successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to create tag.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    },

    async updateTag(tagId, tagData) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.put(`/tags/${tagId}`, tagData);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Tag updated successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to update tag.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    },

    async deleteTag(tagId) {
        const uiStore = useUiStore();
        this.isSaving = true;
        try {
            await apiClient.delete(`/tags/${tagId}`);
            await this.fetchAllTagsData();
            uiStore.showToast({ message: 'Tag deleted successfully.', type: 'success' });
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to delete tag.';
            this.error = errorMessage;
            uiStore.showToast({ message: errorMessage, type: 'error' });
            throw err;
        } finally {
            this.isSaving = false;
        }
    }
  },
});