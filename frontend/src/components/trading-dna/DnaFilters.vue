<template>
  <div class="filters-container">
    <h3 class="filters-title">DNA Explorer</h3>
    <p class="filters-subtitle">Select any combination of labels to analyze your performance.</p>

    <div class="filter-group">
      <label for="tags-filter">Tags</label>
      <BaseMultiSelect
        id="tags-filter"
        v-model="selectedTags"
        :options="tagOptions"
        placeholder="Filter by tags..."
        @update:modelValue="applyFilters"
      />
    </div>

    <div class="filter-group">
      <label for="mistakes-filter">Mistakes</label>
      <BaseMultiSelect
        id="mistakes-filter"
        v-model="selectedMistakes"
        :options="mistakeOptions"
        placeholder="Filter by mistakes..."
        @update:modelValue="applyFilters"
      />
    </div>

    <div class="filter-group">
      <label for="psychology-filter">Psychology States</label>
      <BaseMultiSelect
        id="psychology-filter"
        v-model="selectedPsychology"
        :options="psychologyOptions"
        placeholder="Filter by psychology..."
        @update:modelValue="applyFilters"
      />
    </div>

    <div class="filter-group">
      <label for="news-filter">News Impacts</label>
      <BaseMultiSelect
        id="news-filter"
        v-model="selectedNews"
        :options="newsOptions"
        placeholder="Filter by news impacts..."
      />
    </div>

    <BaseButton @click="applyFilters" :loading="tradingDnaStore.isLoading" class="apply-button">
      Apply Filters
    </BaseButton>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import { useLibraryStore } from '@/stores/libraryStore';
import { useTradingDnaStore } from '@/stores/tradingDnaStore';
import BaseMultiSelect from '@/components/ui/BaseMultiSelect.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

// --- STORES ---
const tagsStore = useTagsStore();
const libraryStore = useLibraryStore();
const tradingDnaStore = useTradingDnaStore();

// --- LOCAL STATE FOR SELECTORS ---
const selectedTags = ref([]);
const selectedMistakes = ref([]);
const selectedPsychology = ref([]);
const selectedNews = ref([]);

// --- DATA FETCHING ---
onMounted(() => {
  // Data is likely already fetched by the parent view, but this ensures it's available
  if (tagsStore.tags.length === 0) tagsStore.fetchAllTagsData();
  if (libraryStore.mistakes.length === 0) libraryStore.fetchAllLibraryData();
});

// --- COMPUTED OPTIONS FOR SELECTORS ---
const toOptions = (items) => items.map(item => ({ value: item.id, label: item.name }));

const tagOptions = computed(() => toOptions(tagsStore.tags));
const mistakeOptions = computed(() => toOptions(libraryStore.mistakes));
const psychologyOptions = computed(() => toOptions(libraryStore.psychologyStates));
const newsOptions = computed(() => toOptions(libraryStore.newsImpacts));

// --- ACTIONS ---
function applyFilters() {
  tradingDnaStore.updateFilters({
    tag_ids: selectedTags.value,
    mistake_ids: selectedMistakes.value,
    psychology_state_ids: selectedPsychology.value,
    news_impact_ids: selectedNews.value,
  });
}
</script>

<style scoped>
.filters-container {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.apply-button {
  margin-top: var(--semantic-size-stack-md);
}

.filters-title {
  font: var(--semantic-font-style-heading-lg);
}

.filters-subtitle {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-top: -12px; /* Pull subtitle closer to title */
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.filter-group label {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}
</style>