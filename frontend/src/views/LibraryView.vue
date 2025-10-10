<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Library</h1>
        <p class="page-subtitle">Manage your Tags, Mistakes, Psychology States, and News Impacts.</p>
      </div>
       <BaseButton v-if="activeTab === 'tags' && !tagsStore.isCreatingGroup" @click="tagsStore.setCreatingGroup(true)">
        <PlusIcon class="w-4 h-4 mr-2" />
        Add Group
      </BaseButton>
    </div>

    <!-- TABS -->
    <BaseTabs v-model="activeTab" :tabs="tabs" />

    <!-- TAB CONTENT -->
    <div class="tab-content">
      <!-- Loading State for Library Data -->
      <div v-if="libraryStore.isLoading && activeTab !== 'tags'" class="loading-state">
        <LoadingSpinner />
      </div>
      <!-- Error State for Library Data -->
      <div v-else-if="libraryStore.error && activeTab !== 'tags'" class="error-state">
        <p>Error loading data: {{ libraryStore.error }}</p>
      </div>

      <!-- Library Content -->
      <div v-else-if="activeTab !== 'tags'" class="content-grid">
        <LibraryManagementCard
          v-if="activeTab === 'mistakes'"
          title="Mistakes"
          :items="libraryStore.mistakes"
          :create-action="libraryStore.createMistake"
          :update-action="libraryStore.updateMistake"
          :delete-action="libraryStore.deleteMistake"
        />
        <LibraryManagementCard
          v-if="activeTab === 'psychology'"
          title="Psychology States"
          :items="libraryStore.psychologyStates"
          :create-action="libraryStore.createPsychologyState"
          :update-action="libraryStore.updatePsychologyState"
          :delete-action="libraryStore.deletePsychologyState"
        />
        <LibraryManagementCard
          v-if="activeTab === 'news'"
          title="News Impacts"
          :items="libraryStore.newsImpacts"
          :create-action="libraryStore.createNewsImpact"
          :update-action="libraryStore.updateNewsImpact"
          :delete-action="libraryStore.deleteNewsImpact"
        />
      </div>

      <!-- Tags Management Tab -->
      <TagManagementTab v-if="activeTab === 'tags'" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useLibraryStore } from '@/stores/libraryStore';
import { useTagsStore } from '@/stores/tagsStore';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import LibraryManagementCard from '@/components/library/LibraryManagementCard.vue';
import TagManagementTab from '@/components/tags/TagManagementTab.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const libraryStore = useLibraryStore();
const tagsStore = useTagsStore();

const activeTab = ref('tags'); // Default to tags tab

const tabs = [
  { id: 'tags', label: 'Tags' },
  { id: 'mistakes', label: 'Mistakes' },
  { id: 'psychology', label: 'Psychology' },
  { id: 'news', label: 'News Impacts' },
];

// Fetch data when the component mounts
onMounted(() => {
  tagsStore.fetchAllTagsData();
  libraryStore.fetchAllLibraryData();
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
.tab-content {
  margin-top: var(--semantic-size-stack-lg);
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