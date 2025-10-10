<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Library & DNA</h1>
        <p class="page-subtitle">Manage your labels and discover the hidden patterns in your trading.</p>
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
      <!-- Loading States -->
      <div v-if="isLoading" class="loading-state">
        <LoadingSpinner />
        <p v-if="activeTab === 'dna'">Analyzing your trades...</p>
      </div>
      <!-- Error States -->
      <div v-else-if="error" class="error-state">
        <p>An error occurred: {{ error }}</p>
      </div>

      <!-- Library Management Content -->
      <div v-else-if="['tags', 'mistakes', 'psychology', 'news'].includes(activeTab)">
        <div v-if="activeTab !== 'tags'" class="content-grid">
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
        <TagManagementTab v-if="activeTab === 'tags'" />
      </div>

      <!-- Trading DNA Content -->
      <div v-else-if="activeTab === 'dna' && dnaStore.report" class="main-content">
        <div class="section-container">
          <h2 class="section-title">Key Insights</h2>
          <div class="insights-grid">
            <ComboCard v-for="(combo, index) in dnaStore.report.golden_combos" :key="`golden-${index}`" title="Golden Combo" :combo="combo" type="golden" />
            <ComboCard v-for="(combo, index) in dnaStore.report.toxic_combos" :key="`toxic-${index}`" title="Toxic Combo" :combo="combo" type="toxic" />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useLibraryStore } from '@/stores/libraryStore';
import { useTagsStore } from '@/stores/tagsStore';
import { useTradingDnaStore } from '@/stores/tradingDnaStore';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import LibraryManagementCard from '@/components/library/LibraryManagementCard.vue';
import TagManagementTab from '@/components/tags/TagManagementTab.vue';
import ComboCard from '@/components/trading-dna/ComboCard.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const libraryStore = useLibraryStore();
const tagsStore = useTagsStore();
const dnaStore = useTradingDnaStore();

const activeTab = ref('tags');

const tabs = [
  { id: 'tags', label: 'Tags' },
  { id: 'mistakes', label: 'Mistakes' },
  { id: 'psychology', label: 'Psychology' },
  { id: 'news', label: 'News Impacts' },
  { id: 'dna', label: 'Trading DNA' },
];

const isLoading = computed(() => {
  if (activeTab.value === 'dna') return dnaStore.isLoading && !dnaStore.report;
  if (activeTab.value === 'tags') return tagsStore.isLoading;
  return libraryStore.isLoading;
});

const error = computed(() => {
  if (activeTab.value === 'dna') return dnaStore.error;
  if (activeTab.value === 'tags') return tagsStore.error;
  return libraryStore.error;
});

onMounted(() => {
  tagsStore.fetchAllTagsData();
  libraryStore.fetchAllLibraryData();
  dnaStore.fetchTradingDnaReport();
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  gap: var(--semantic-size-stack-md);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--semantic-size-stack-lg);
}

/* Styles from TradingDnaView */
.section-container {
  margin-bottom: var(--semantic-size-stack-xl);
}
.section-title {
  font: var(--semantic-font-style-heading-xl);
  margin-bottom: var(--semantic-size-stack-md);
}
.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
.explorer-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--semantic-size-stack-lg);
  align-items: start;
}
.explorer-main {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
</style>