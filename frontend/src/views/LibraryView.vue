<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Libreria</h1>
        <p class="page-subtitle">Create and manage all your labels: tags, mistakes, and more.</p>
      </div>
      <BaseButton @click="tagsStore.setCreatingGroup(true)" v-if="activeTab === 'tags' && !tagsStore.isCreatingGroup">
        <PlusIcon class="w-4 h-4 mr-2" />
        Add Group
      </BaseButton>
    </div>

    <!-- TABS -->
    <BaseTabs v-model="activeTab" :tabs="tabs" />

    <!-- TAB CONTENT -->
    <div class="tab-content">
      <TagManagementTab v-if="activeTab === 'tags'" />

      <SimpleLabelCard
        v-if="activeTab === 'mistakes'"
        title="Mistakes"
        item-type-name="Mistake"
        :items="mistakesStore.mistakes"
        :is-loading="mistakesStore.isLoading"
        :is-saving="mistakesStore.isSaving"
        @create-item="mistakesStore.createMistake($event)"
        @update-item="mistakesStore.updateMistake($event.id, $event)"
        @delete-item="mistakesStore.deleteMistake($event)"
      />

      <SimpleLabelCard
        v-if="activeTab === 'psychology'"
        title="Psychological States"
        item-type-name="State"
        :items="psychologyStore.psychologyStates"
        :is-loading="psychologyStore.isLoading"
        :is-saving="psychologyStore.isSaving"
        @create-item="psychologyStore.createPsychologyState($event)"
        @update-item="psychologyStore.updatePsychologyState($event.id, $event)"
        @delete-item="psychologyStore.deletePsychologyState($event)"
      />

      <SimpleLabelCard
        v-if="activeTab === 'news'"
        title="News Impacts"
        item-type-name="Impact"
        :items="newsImpactsStore.newsImpacts"
        :is-loading="newsImpactsStore.isLoading"
        :is-saving="newsImpactsStore.isSaving"
        @create-item="newsImpactsStore.createNewsImpact($event)"
        @update-item="newsImpactsStore.updateNewsImpact($event.id, $event)"
        @delete-item="newsImpactsStore.deleteNewsImpact($event)"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import { useMistakesStore } from '@/stores/mistakesStore';
import { usePsychologyStatesStore } from '@/stores/psychologyStatesStore';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import TagManagementTab from '@/components/tags/TagManagementTab.vue';
import SimpleLabelCard from '@/components/library/SimpleLabelCard.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const tagsStore = useTagsStore();
const mistakesStore = useMistakesStore();
const psychologyStore = usePsychologyStatesStore();
const newsImpactsStore = useNewsImpactsStore();

const activeTab = ref('tags'); // Default to the tags tab

onMounted(() => {
  mistakesStore.fetchAllMistakes();
  psychologyStore.fetchAllPsychologyStates();
  newsImpactsStore.fetchAllNewsImpacts();
});

const tabs = [
  { id: 'tags', label: 'Setup / Tags' },
  { id: 'mistakes', label: 'Errori' },
  { id: 'psychology', label: 'Stati Psicologici' },
  { id: 'news', label: 'Impatto News' },
];
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
</style>