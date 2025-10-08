<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Tags Settings</h1>
        <p class="page-subtitle">Manage your tags and tag groups here.</p>
      </div>
      <BaseButton @click="store.setCreatingGroup(true)" v-if="!store.isCreatingGroup">
        <PlusIcon class="w-4 h-4 mr-2" />
        Add Group
      </BaseButton>
    </div>

    <!-- INLINE GROUP CREATOR -->
    <GroupCreator v-if="store.isCreatingGroup" />

    <!-- LOADING/ERROR STATES -->
    <div v-if="isLoading" class="loading-state"><LoadingSpinner /></div>
    <div v-else-if="error" class="error-state"><p>Error loading tags: {{ error }}</p></div>

    <!-- CONTENT -->
    <div v-else class="content-container">
      <TagGroup
        v-for="group in groupedTags"
        :key="group.id"
        :group="group"
      />
      <div v-if="!groupedTags.length && !store.isCreatingGroup" class="empty-state">
        <p>No tag groups have been created yet.</p>
        <p>Click "+ Add Group" to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import GroupCreator from '@/components/tags/GroupCreator.vue';
import TagGroup from '@/components/tags/TagGroup.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const store = useTagsStore();
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);
const groupedTags = computed(() => store.groupedTags);

onMounted(() => {
  store.fetchAllTagsData();
  // Ensure creator is hidden on mount
  store.setCreatingGroup(false);
  store.setCreatingTagInGroup(null);
});
</script>

<style scoped>
.page-container {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-spacing-lg);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.content-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--semantic-size-spacing-lg);
}
.empty-state {
  text-align: center;
  padding: 4rem;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}
</style>