<script setup>
import { onMounted } from "vue";
import { useTagsStore } from "@/stores/tagsStore";
import TagGroupCard from "@/components/tags/TagGroupCard.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";

const tagsStore = useTagsStore();

onMounted(() => {
  // Fetch only if data is not already present
  if (tagsStore.tagsGroups.length === 0 || tagsStore.tags.length === 0) {
    tagsStore.fetchAll();
  }
});
</script>

<template>
  <div class="tags-settings-view">
    <header class="view-header">
      <h1>Tags Settings</h1>
      <p>Organize and manage your tags and groups.</p>
    </header>

    <div v-if="tagsStore.isLoading" class="loading-container">
      <LoadingSpinner />
    </div>

    <div v-else-if="tagsStore.error" class="error-container">
      <p>{{ tagsStore.error }}</p>
    </div>

    <div v-else class="groups-grid">
      <TagGroupCard
        v-for="group in tagsStore.tagsGroups"
        :key="group.id"
        :group="group"
        :tags="tagsStore.getTagsByGroupId(group.id)"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tags-settings-view {
  padding: var(--semantic-size-inset-lg);
}

.view-header {
  margin-bottom: var(--semantic-size-stack-xl);
  h1 {
    font: var(--semantic-font-style-heading-2xl);
    color: var(--semantic-color-text-primary);
  }
  p {
    font: var(--semantic-font-style-body-md);
    color: var(--semantic-color-text-secondary);
  }
}

.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
</style>