<template>
  <div class="news-impact-management-container">
    <!-- INLINE GROUP CREATOR -->
    <GroupCreator v-if="store.isCreatingGroup" />

    <!-- LOADING/ERROR STATES -->
    <div v-if="isLoading" class="loading-state"><LoadingSpinner /></div>
    <div v-else-if="error" class="error-state"><p>Error loading news impacts: {{ error }}</p></div>

    <!-- CONTENT -->
    <div
      v-else
      class="content-container"
    >
      <NewsImpactGroup v-for="group in store.groupedNewsImpacts" :key="group.id" :group="group" />
    </div>
    <div v-if="!store.groupedNewsImpacts.length && !store.isCreatingGroup && !isLoading" class="empty-state">
        <p>No news impact groups have been created yet.</p>
        <p>Click "+ Add Group" to get started.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import GroupCreator from '@/components/news-impacts/NewsImpactGroupCreator.vue';
import NewsImpactGroup from '@/components/news-impacts/NewsImpactGroup.vue';

const store = useNewsImpactsStore();
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

onMounted(() => {
  // Data is fetched by the parent LibraryView, so no need to fetch here
  // Ensure creator is hidden on mount
  store.setCreatingGroup(false);
  store.setCreatingTagInGroup(null);
});
</script>

<style scoped>
.news-impact-management-container {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
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
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}
</style>