import { defineStore } from 'pinia';
import api from '../services/api';
import { ref } from 'vue';

export const useTagsStore = defineStore('tags', () => {
  // --- STATE ---
  const tags = ref([]);
  const tagGroups = ref([]);

  // --- ACTIONS ---

  /**
   * Fetches all tags for the current user from the API.
   */
  async function fetchTags() {
    try {
      const response = await api.get('/me/tags');
      tags.value = response.data;
    } catch (error) {
      console.error('Error fetching tags:', error);
      // Here you could add a toast notification for the user
    }
  }

  /**
   * Fetches all tag groups for the current user from the API.
   */
  async function fetchTagGroups() {
    try {
      const response = await api.get('/tags-groups');
      tagGroups.value = response.data;
    } catch (error) {
      console.error('Error fetching tag groups:', error);
      // Here you could add a toast notification for the user
    }
  }

  // --- GETTERS ---
  // (Can be added later if needed)

  return {
    tags,
    tagGroups,
    fetchTags,
    fetchTagGroups,
  };
});