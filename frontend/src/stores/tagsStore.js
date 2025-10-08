import { defineStore } from 'pinia';
import api from '../services/api';
import { ref } from 'vue';

export const useTagsStore = defineStore('tags', () => {
  // --- STATE ---
  const tags = ref([]);
  const tagGroups = ref([]);

  // --- ACTIONS ---

  async function fetchTags() {
    try {
      const response = await api.get('/me/tags');
      tags.value = response.data;
    } catch (error) {
      console.error('Error fetching tags:', error);
    }
  }

  async function fetchTagGroups() {
    try {
      const response = await api.get('/tags-groups/');
      tagGroups.value = response.data;
    } catch (error) {
      console.error('Error fetching tag groups:', error);
    }
  }

  async function createTagGroup(groupData) {
    try {
      const response = await api.post('/tags-groups/', groupData);
      tagGroups.value.unshift(response.data);
    } catch (error) {
      console.error('Error creating tag group:', error);
      throw error;
    }
  }

  async function updateTagGroup(groupId, groupData) {
    try {
      const response = await api.put(`/tags-groups/${groupId}/`, groupData);
      const index = tagGroups.value.findIndex(g => g.id === groupId);
      if (index !== -1) {
        tagGroups.value[index] = response.data;
      }
    } catch (error) {
      console.error('Error updating tag group:', error);
      throw error;
    }
  }

  async function deleteTagGroup(groupId) {
    try {
      await api.delete(`/tags-groups/${groupId}/`);
      // Remove the group itself
      tagGroups.value = tagGroups.value.filter(g => g.id !== groupId);
      // Also remove the tags that belonged to this group from the local state
      tags.value = tags.value.filter(t => t.tags_group_id !== groupId);
    } catch (error) {
      console.error('Error deleting tag group:', error);
      throw error;
    }
  }

  async function createTag(tagData) {
    try {
      const response = await api.post('/me/tags', tagData);
      tags.value.push(response.data);
    } catch (error) {
      console.error('Error creating tag:', error);
      throw error;
    }
  }

  async function updateTag(tagId, tagData) {
    try {
      const response = await api.put(`/tags/${tagId}`, tagData);
      const index = tags.value.findIndex(t => t.id === tagId);
      if (index !== -1) {
        tags.value[index] = response.data;
      }
    } catch (error) {
      console.error('Error updating tag:', error);
      throw error;
    }
  }

  async function deleteTag(tagId) {
    try {
      await api.delete(`/tags/${tagId}`);
      tags.value = tags.value.filter(t => t.id !== tagId);
    } catch (error) {
      console.error('Error deleting tag:', error);
      throw error;
    }
  }

  return {
    tags,
    tagGroups,
    fetchTags,
    fetchTagGroups,
    createTagGroup,
    updateTagGroup,
    deleteTagGroup,
    createTag,
    updateTag,
    deleteTag,
  };
});