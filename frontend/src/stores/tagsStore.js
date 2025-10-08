import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

export const useTagsStore = defineStore('tags', () => {
  // --- STATE ---
  const tags = ref([]);
  const tagGroups = ref([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref(null);
  const isCreatingGroup = ref(false);
  const creatingTagInGroupId = ref(null);

  // --- ACTIONS ---
  function setCreatingGroup(status) {
    isCreatingGroup.value = status;
  }

  function setCreatingTagInGroup(groupId) {
    creatingTagInGroupId.value = groupId;
  }

  // --- GETTERS ---
  const groupedTags = computed(() => {
    if (!tagGroups.value.length) {
      return [];
    }
    return tagGroups.value.map(group => ({
      ...group,
      tags: tags.value.filter(tag => tag.group_id === group.id),
    }));
  });

  // --- ACTIONS ---
  async function fetchTags() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log("User not authenticated. Skipping tags fetch.");
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/me/tags');
      tags.value = response.data;
    } catch (err) {
      console.error('Error fetching tags:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      tags.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTagGroups() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log("User not authenticated. Skipping tag groups fetch.");
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/tags-groups');
      tagGroups.value = response.data;
    } catch (err) {
      console.error('Error fetching tag groups:', err);
      error.value = err.response?.data?.detail || 'An unexpected error occurred.';
      tagGroups.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchAllTagsData() {
      isLoading.value = true;
      error.value = null;
      try {
          await Promise.all([fetchTags(), fetchTagGroups()]);
      } catch (err) {
          console.error('Error fetching all tags data:', err);
          error.value = 'An error occurred while fetching tags information.';
      } finally {
          isLoading.value = false;
      }
  }

  // --- GROUP ACTIONS ---
  async function createTagGroup(groupData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.post('/tags-groups', groupData);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Group created successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updateTagGroup(groupId, groupData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/tags-groups/${groupId}`, groupData);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Group updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deleteTagGroup(groupId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/tags-groups/${groupId}`);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Group deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete group.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- TAG ACTIONS ---
  async function createTag(tagData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.post('/me/tags', tagData);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Tag created successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to create tag.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function updateTag(tagId, tagData) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.put(`/tags/${tagId}`, tagData);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Tag updated successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to update tag.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  async function deleteTag(tagId) {
      const uiStore = useUiStore();
      isSaving.value = true;
      try {
          await apiClient.delete(`/tags/${tagId}`);
          await fetchAllTagsData();
          uiStore.showNotification({ message: 'Tag deleted successfully.', type: 'success' });
      } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete tag.';
          error.value = errorMessage;
          uiStore.showNotification({ message: errorMessage, type: 'error' });
          throw err;
      } finally {
          isSaving.value = false;
      }
  }

  // --- EXPORT ---
  return {
    tags,
    tagGroups,
    isLoading,
    isSaving,
    error,
    isCreatingGroup,
    creatingTagInGroupId,
    setCreatingGroup,
    setCreatingTagInGroup,
    groupedTags,
    fetchAllTagsData,
    createTagGroup,
    updateTagGroup,
    deleteTagGroup,
    createTag,
    updateTag,
    deleteTag,
  };
});