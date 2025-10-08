import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tags: [],
    tagGroups: [],
    isLoading: false,
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
        const response = await apiClient.get('/me/tags-groups');
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
    }
  },
});