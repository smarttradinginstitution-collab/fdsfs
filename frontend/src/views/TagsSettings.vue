<template>
  <div class="page-container">
    <div class="header">
      <h1 class="page-title">Tags Settings</h1>
      <p class="page-subtitle">Manage your tags and tag groups here.</p>
    </div>

    <!-- Loading and Error States -->
    <div v-if="isLoading" class="loading-state">
      <LoadingSpinner />
    </div>
    <div v-else-if="error" class="error-state">
      <p>Error loading tags: {{ error }}</p>
    </div>

    <!-- Content Grid -->
    <div v-else class="content-grid">
      <BaseWidget v-for="group in groupedTags" :key="group.id" class="tag-group-card">
        <template #header>
          <h2 class="group-title">{{ group.name_group }}</h2>
        </template>

        <div class="tags-container">
          <BasePill
            v-for="tag in group.tags"
            :key="tag.id"
            :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }"
            class="tag-pill"
          >
            {{ tag.name }}
          </BasePill>
        </div>
      </BaseWidget>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useTagsStore } from '@/stores/tagsStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import BasePill from '@/components/ui/BasePill.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const tagsStore = useTagsStore();
const { groupedTags, isLoading, error } = storeToRefs(tagsStore);

onMounted(() => {
  tagsStore.fetchAllTagsData();
});

// Simple utility to determine text color based on background brightness
const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff'; // Default to white for safety
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16); // hexToR
  const g = parseInt(color.substring(2, 4), 16); // hexToG
  const b = parseInt(color.substring(4, 6), 16); // hexToB
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff'; // Return black for light colors, white for dark
};
</script>

<style scoped>
.page-container {
  padding: var(--semantic-size-inset-lg);
}

.header {
  margin-bottom: var(--semantic-size-spacing-lg);
}

.page-title {
  font: var(--semantic-font-style-heading-2);
  color: var(--semantic-color-text-primary);
}

.page-subtitle {
  font: var(--semantic-font-style-body-md);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--base-size-spacing-1);
}

.loading-state, .error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--semantic-size-spacing-lg);
}

.tag-group-card .group-title {
  font: var(--semantic-font-style-heading-4);
  color: var(--semantic-color-text-primary);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--base-size-spacing-2);
  padding-top: var(--semantic-size-inset-lg); /* Add padding as it was removed in the widget */
}

.tag-pill {
  font-weight: 600; /* Make text a bit bolder */
}
</style>