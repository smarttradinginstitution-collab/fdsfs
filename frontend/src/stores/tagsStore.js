import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api";
import { useGeneralAccountStore } from "@/stores/generalAccountStore";

export const useTagsStore = defineStore("tags", () => {
  const generalAccountStore = useGeneralAccountStore();

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
    if (!generalAccountStore.generalAccount.id) return;
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
    if (!generalAccountStore.generalAccount.id) return;
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
    await Promise.all([fetchTags(), fetchTagsGroups()]);
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
  };
});