<script setup>
import { onMounted, computed } from 'vue';
import { useTagsStore } from '../stores/tagsStore';
import MainLayout from '../components/layout/MainLayout.vue';
import BaseWidget from '../components/layout/BaseWidget.vue';

// --- STORE ---
const tagsStore = useTagsStore();

// --- LIFECYCLE HOOKS ---
onMounted(() => {
  tagsStore.fetchTagGroups();
  tagsStore.fetchTags();
});

// --- COMPUTED PROPERTIES ---
const tagGroups = computed(() => tagsStore.tagGroups);
const tags = computed(() => tagsStore.tags);

// Helper to get tags for a specific group
const getTagsForGroup = (groupId) => {
  return tags.value.filter(tag => tag.tags_group_id === groupId);
};
</script>

<template>
  <MainLayout>
    <div class="tags-settings-page">
      <h1>Tags Settings</h1>
      <p class="page-description">Here you can manage your tags and tag groups.</p>

      <div class="groups-container">
        <BaseWidget
          v-for="group in tagGroups"
          :key="group.id"
          class="tag-group-card"
        >
          <template #title>{{ group.name_group }}</template>
          <div class="tags-list">
            <span
              v-for="tag in getTagsForGroup(group.id)"
              :key="tag.id"
              class="tag-chip"
              :style="{ backgroundColor: tag.color || '#cccccc' }"
            >
              {{ tag.name_tag }}
            </span>
            <span v-if="getTagsForGroup(group.id).length === 0" class="no-tags-message">
              No tags in this group yet.
            </span>
          </div>
        </BaseWidget>
      </div>
    </div>
  </MainLayout>
</template>

<style lang="scss" scoped>
.tags-settings-page {
  padding: var(--semantic-size-inset-lg);
}

h1 {
  font: var(--semantic-font-style-heading-2xl);
  margin-bottom: var(--semantic-size-stack-xs);
}

.page-description {
  font: var(--semantic-font-style-body-md);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-lg);
}

.groups-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.tag-group-card {
  // BaseWidget provides the main structure and styling
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}

.tag-chip {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-pill);
  font: var(--semantic-font-style-label-sm);
  color: var(--base-color-gray-900); // Dark text for contrast on light backgrounds
  font-weight: var(--base-font-weight-medium);
}

.no-tags-message {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
}
</style>