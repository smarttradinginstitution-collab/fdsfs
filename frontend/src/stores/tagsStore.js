import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

export const useTagsStore = defineStore("tags", () => {
  const authStore = useAuthStore();

  // State
  const tags = ref([]);
  const tagsGroups = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const getTagsByGroupId = computed(() => {
    return (groupId) =>
      tags.value.filter((tag) => tag.tags_group_id === groupId);
  });

  // Actions
  async function fetchTags() {
    if (!authStore.generalAccount?.id) return;
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get("/me/tags");
      tags.value = response.data;
    } catch (e) {
      error.value = "Failed to fetch tags.";
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTagsGroups() {
    if (!authStore.generalAccount?.id) return;
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get("/tags-groups/");
      tagsGroups.value = response.data;
    } catch (e) {
      error.value = "Failed to fetch tag groups.";
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  // Combined action
  async function fetchAll() {
    // Reset state to avoid showing stale data from another account
    tags.value = [];
    tagsGroups.value = [];
    await Promise.all([fetchTags(), fetchTagsGroups()]);
  }

  // --- TAG GROUP ACTIONS ---

  async function createTagGroup(groupData) {
    try {
      const response = await api.post("/tags-groups/", groupData);
      tagsGroups.value.push(response.data);
      return response.data;
    } catch (e) {
      console.error("Failed to create tag group:", e);
      throw e; // Re-throw to be handled by the component
    }
  }

  async function updateTagGroup(groupId, groupData) {
    try {
      const response = await api.put(`/tags-groups/${groupId}`, groupData);
      const index = tagsGroups.value.findIndex((g) => g.id === groupId);
      if (index !== -1) {
        tagsGroups.value[index] = response.data;
      }
      return response.data;
    } catch (e) {
      console.error("Failed to update tag group:", e);
      throw e;
    }
  }

  async function deleteTagGroup(groupId) {
    try {
      await api.delete(`/tags-groups/${groupId}`);
      tagsGroups.value = tagsGroups.value.filter((g) => g.id !== groupId);
      // Also remove associated tags from the local state
      tags.value = tags.value.filter((t) => t.tags_group_id !== groupId);
    } catch (e) {
      console.error("Failed to delete tag group:", e);
      throw e;
    }
  }

  // --- TAG ACTIONS ---

  async function createTag(tagData) {
    try {
      const response = await api.post("/me/tags", tagData);
      tags.value.push(response.data);
      return response.data;
    } catch (e) {
      console.error("Failed to create tag:", e);
      throw e;
    }
  }

  async function updateTag(tagId, tagData) {
    try {
      const response = await api.put(`/tags/${tagId}`, tagData);
      const index = tags.value.findIndex((t) => t.id === tagId);
      if (index !== -1) {
        tags.value[index] = response.data;
      }
      return response.data;
    } catch (e) {
      console.error("Failed to update tag:", e);
      throw e;
    }
  }

  async function deleteTag(tagId) {
    try {
      await api.delete(`/tags/${tagId}`);
      tags.value = tags.value.filter((t) => t.id !== tagId);
    } catch (e) {
      console.error("Failed to delete tag:", e);
      throw e;
    }
  }

  return {
    // State
    tags,
    tagsGroups,
    isLoading,
    error,

    // Getters
    getTagsByGroupId,

    // Actions
    fetchTags,
    fetchTagsGroups,
    fetchAll,
    createTagGroup,
    updateTagGroup,
    deleteTagGroup,
    createTag,
    updateTag,
    deleteTag,
  };
});