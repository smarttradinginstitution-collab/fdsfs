<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Library</h1>
        <p class="page-subtitle">Manage your Mistakes, Psychology States, and News Impacts.</p>
      </div>
    </div>

    <!-- LOADING STATE -->
    <div v-if="store.isLoading" class="loading-state">
      <LoadingSpinner />
    </div>

    <!-- ERROR STATE -->
    <div v-else-if="store.error" class="error-state">
      <p>Error loading library data: {{ store.error }}</p>
    </div>

    <!-- CONTENT -->
    <div v-else class="content-grid">
      <LibraryManagementCard
        title="Mistakes"
        :items="store.mistakes"
        :create-action="store.createMistake"
        :update-action="store.updateMistake"
        :delete-action="store.deleteMistake"
      />
      <LibraryManagementCard
        title="Psychology States"
        :items="store.psychologyStates"
        :create-action="store.createPsychologyState"
        :update-action="store.updatePsychologyState"
        :delete-action="store.deletePsychologyState"
      />
      <LibraryManagementCard
        title="News Impacts"
        :items="store.newsImpacts"
        :create-action="store.createNewsImpact"
        :update-action="store.updateNewsImpact"
        :delete-action="store.deleteNewsImpact"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useLibraryStore } from '@/stores/libraryStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import LibraryManagementCard from '@/components/library/LibraryManagementCard.vue';

const store = useLibraryStore();

onMounted(() => {
  store.fetchAllLibraryData();
});
</script>

<style scoped>
.page-container {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.page-title {
  font: var(--semantic-font-style-heading-2xl);
}
.page-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xxs);
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
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
</style>