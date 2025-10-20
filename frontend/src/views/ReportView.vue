<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import TradeStats from '@/components/reports/TradeStats.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import EditTradeDetailsModal from '@/components/reports/EditTradeDetailsModal.vue';
import TradeImageGallery from '@/components/images/TradeImageGallery.vue';
import ImageMetadataModal from '@/components/images/ImageMetadataModal.vue';
import ImageLightbox from '@/components/images/ImageLightbox.vue';
import TradeNoteEditor from '@/components/reports/TradeNoteEditor.vue';
import PlaybookTab from '@/components/reports/PlaybookTab.vue';
import { useTradesStore } from '@/stores/trades';
import { useImageStore } from '@/stores/imageStore';
import { useNotebookStore } from '@/stores/notebookStore';
import { useLoadingStore } from '@/stores/loadingStore';
import { storeToRefs } from 'pinia';

// --- STATE ---
const route = useRoute();
const router = useRouter();
const tradesStore = useTradesStore();
const imageStore = useImageStore();
const notebookStore = useNotebookStore();
const loadingStore = useLoadingStore();

const activeTab = ref('stats');
const isEditModalOpen = ref(false);
const isMetadataModalOpen = ref(false);
const selectedImageForEdit = ref(null);
const isLightboxOpen = ref(false);
const lightboxCurrentIndex = ref(0);
const error = ref(null);

// --- Advanced Performance State ---
const tradeDataCache = ref({});
const isNoteLoading = ref(false);

const leftColumnTabs = [
  { id: 'stats', label: 'Stats' },
  { id: 'playbook', label: 'Playbook' },
  { id: 'executions', label: 'Executions' },
  { id: 'attachments', label: 'Attachments' },
];

// --- COMPUTED ---
const trade = computed(() => tradesStore.selectedTrade);
const { imagesForCurrentTrade } = storeToRefs(imageStore);
const { selectedNote } = storeToRefs(notebookStore);

const primaryBeforeImage = computed(() => Array.isArray(imagesForCurrentTrade.value) ? imagesForCurrentTrade.value.find(img => img.is_primary_before) : null);
const primaryAfterImage = computed(() => Array.isArray(imagesForCurrentTrade.value) ? imagesForCurrentTrade.value.find(img => img.is_primary_after) : null);

const tradeDate = computed(() => {
  if (!trade.value?.entry_timestamp) return '';
  const date = new Date(trade.value.entry_timestamp);
  return date.toLocaleDateString('en-US', {
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
  });
});

// --- METHODS ---

const handleNavigation = (targetId) => {
  if (targetId) router.push({ name: 'report-detail', params: { id: targetId } });
};

const handlePrevious = () => handleNavigation(tradesStore.getPreviousTradeId);
const handleNext = () => handleNavigation(tradesStore.getNextTradeId);

const openEditModal = () => { isEditModalOpen.value = true; };

const handleEditImage = (image) => {
  selectedImageForEdit.value = image;
  isMetadataModalOpen.value = true;
};

const handleUpdateTradeDetails = async (payload) => {
  if (trade.value) {
    await tradesStore.updateTrade(trade.value.id, payload);
    tradeDataCache.value[trade.value.id] = undefined; // Invalidate cache
    await tradesStore.fetchAllDataForDashboard();
  }
};

const openLightbox = (index) => {
  lightboxCurrentIndex.value = index;
  isLightboxOpen.value = true;
};

const prefetchTradeData = async (tradeId) => {
  if (!tradeId || tradeDataCache.value[tradeId]) {
    return;
  }
  try {
    const [fetchedTrade, fetchedImages, fetchedNote] = await Promise.all([
      tradesStore.fetchTradeById(tradeId),
      imageStore.fetchImagesForTrade(tradeId),
      notebookStore.fetchNoteByTradeId(tradeId),
    ]);

    if (fetchedTrade && fetchedTrade.id) {
      tradeDataCache.value[tradeId] = {
        trade: fetchedTrade,
        images: fetchedImages,
        note: fetchedNote,
      };
    }
  } catch (e) {
    console.error(`Failed to prefetch data for trade ${tradeId}:`, e);
    // Do not pollute cache with failed attempts
  }
};

const selectTradeFromStore = async (tradeId) => {
  error.value = null;

  // 1. Check cache first
  const cachedData = tradeDataCache.value[tradeId];
  if (cachedData && cachedData.trade) {
    tradesStore.selectedTrade = cachedData.trade;
    imageStore.imagesForCurrentTrade = cachedData.images;
    notebookStore.selectedNote = cachedData.note;
    return; // Instant navigation
  }

  // 2. If not in cache, fetch data
  loadingStore.startLoading();
  isNoteLoading.value = true;
  tradesStore.selectedTrade = null; // Clear previous trade to prevent flicker

  try {
    const [fetchedTrade, fetchedImages, fetchedNote] = await Promise.all([
      tradesStore.fetchTradeById(tradeId),
      imageStore.fetchImagesForTrade(tradeId),
      notebookStore.fetchNoteByTradeId(tradeId),
    ]);

    if (!fetchedTrade) {
      throw new Error("Trade data could not be fetched.");
    }

    // 3. Update state and populate cache
    tradesStore.selectedTrade = fetchedTrade;
    imageStore.imagesForCurrentTrade = fetchedImages;
    notebookStore.selectedNote = fetchedNote;

    tradeDataCache.value[tradeId] = {
      trade: fetchedTrade,
      images: fetchedImages,
      note: fetchedNote,
    };

    // 4. Trigger pre-fetching for next/prev trades
    prefetchTradeData(tradesStore.getNextTradeId);
    prefetchTradeData(tradesStore.getPreviousTradeId);

  } catch (e) {
    console.error("Error loading trade:", e);
    error.value = "Could not load trade data.";
    tradesStore.selectedTrade = null;
  } finally {
    loadingStore.stopLoading();
    isNoteLoading.value = false;
  }
};

// --- LIFECYCLE & WATCHERS ---
watch(() => route.params.id, (newId) => {
  if (newId) {
    selectTradeFromStore(newId);
  }
}, { immediate: true });

</script>

<template>
  <div class="report-detail-view">
    <template v-if="!loadingStore.isLoading">
      <div v-if="error" class="error-state">
        <h2>Error</h2>
        <p>{{ error }}</p>
        <BaseButton @click="router.push({ name: 'trades' })">Back to Trades</BaseButton>
      </div>
      <div v-else-if="trade" class="report-container">
        <header class="report-header">
          <div class="navigation-controls">
            <button @click="handlePrevious" class="nav-button" :disabled="!tradesStore.getPreviousTradeId">&lt;</button>
            <button @click="handleNext" class="nav-button" :disabled="!tradesStore.getNextTradeId">&gt;</button>
          </div>
          <div class="trade-identifier">
            <h1 class="asset-name">{{ trade.symbol_snapshot }}</h1>
            <p class="trade-date">{{ tradeDate }}</p>
          </div>
          <div class="action-buttons">
            <button class="action-button">Mark as reviewed</button>
            <button class="action-button">Replay</button>
            <button class="action-button">Share</button>
          </div>
        </header>

        <main class="report-content">
          <div class="left-column">
            <BaseWidget class="stats-widget">
              <BaseTabs v-model="activeTab" :tabs="leftColumnTabs">
                <template #stats>
                  <TradeStats :trade="trade" @open-edit-modal="openEditModal" />
                </template>
                <template #playbook>
                  <PlaybookTab :trade="trade" />
                </template>
                <template #executions>
                  <div>Contenuto Executions</div>
                </template>
                <template #attachments>
                  <TradeImageGallery
                    :trade-id="trade.id"
                    :images="imagesForCurrentTrade"
                    mode="uploader-only"
                    :allow-insertion="false"
                    @edit-image="handleEditImage"
                  />
                </template>
              </BaseTabs>
            </BaseWidget>
          </div>

          <div class="right-column">
            <TradeNoteEditor
              :trade-id="trade.id"
              :trade-details="trade"
              :initial-note="selectedNote"
              :is-loading="isNoteLoading"
            />
            <BaseWidget class="visual-analysis-widget">
              <h3 class="widget-title">Visual Analysis</h3>
              <div v-if="primaryBeforeImage || primaryAfterImage" class="chart-comparison">
                <div class="chart-container">
                  <h4>Before</h4>
                  <img v-if="primaryBeforeImage" :src="primaryBeforeImage.url" alt="Before chart" />
                  <div v-else class="placeholder">Not set</div>
                </div>
                <div class="chart-container">
                  <h4>After</h4>
                  <img v-if="primaryAfterImage" :src="primaryAfterImage.url" alt="After chart" />
                  <div v-else class="placeholder">Not set</div>
                </div>
              </div>
              <hr v-if="primaryBeforeImage || primaryAfterImage" class="section-divider" />
              <TradeImageGallery
                :trade-id="trade.id"
                :images="imagesForCurrentTrade"
                mode="gallery-only"
                :allow-insertion="false"
                @edit-image="handleEditImage"
                @open-lightbox="openLightbox"
              />
            </BaseWidget>
          </div>
        </main>
      </div>
      <div v-else class="not-found-state">
        <h2>Trade Not Found</h2>
        <p>The requested trade could not be found.</p>
        <BaseButton @click="router.push({ name: 'trades' })">Back to Trades</BaseButton>
      </div>
    </template>
    <EditTradeDetailsModal v-if="trade" v-model="isEditModalOpen" :trade="trade" @save="handleUpdateTradeDetails" />
    <ImageMetadataModal :show="isMetadataModalOpen" :image="selectedImageForEdit" @close="isMetadataModalOpen = false" />
    <ImageLightbox v-if="imagesForCurrentTrade && imagesForCurrentTrade.length > 0" :images="imagesForCurrentTrade" :current-index="lightboxCurrentIndex" :show="isLightboxOpen" @close="isLightboxOpen = false" @next="lightboxCurrentIndex = (lightboxCurrentIndex + 1) % imagesForCurrentTrade.length" @prev="lightboxCurrentIndex = (lightboxCurrentIndex - 1 + imagesForCurrentTrade.length) % imagesForCurrentTrade.length" />
  </div>
</template>

<style lang="scss" scoped>
.report-detail-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--semantic-size-inset-lg);
  gap: var(--semantic-size-gap-lg);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--semantic-size-inset-lg);
}

.navigation-controls,
.action-buttons {
  display: flex;
  gap: var(--semantic-size-stack-sm);
}

.trade-identifier {
  text-align: center;
  .asset-name {
    font: var(--semantic-font-style-heading-xl);
    color: var(--semantic-color-text-primary);
  }
  .trade-date {
    font: var(--semantic-font-style-body-sm);
    color: var(--semantic-color-text-secondary);
  }
}

.nav-button, .action-button {
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
  border: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
  cursor: pointer;
  font: var(--semantic-font-style-button-label-medium);
  transition: background-color 0.2s ease;

  &:hover:not(:disabled) {
    background-color: var(--semantic-color-surface-secondary);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.report-content {
  display: flex;
  flex-grow: 1;
  gap: var(--semantic-size-stack-lg);
  min-height: 0;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: var(--semantic-size-stack-lg);
}

.left-column {
  flex: 0 0 33%;
}

.right-column {
  flex: 1;
}

.stats-widget,
.visual-analysis-widget {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-lg);
}

.visual-analysis-widget {
  flex-grow: 2; /* Make notes widget larger */
}

.visual-analysis-widget {
  .widget-title {
    font: var(--semantic-font-style-heading-md);
    margin-bottom: var(--semantic-size-stack-md);
  }
}

.chart-comparison {
  display: flex;
  gap: var(--semantic-size-gap-lg);
}

.chart-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);

  h4 {
    font: var(--semantic-font-style-label-lg);
    color: var(--semantic-color-text-secondary);
  }

  img {
    width: 100%;
    height: auto;
    border-radius: var(--semantic-border-radius-container);
    border: 1px solid var(--semantic-color-border-default);
  }

  .placeholder {
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: var(--semantic-border-radius-container);
    background-color: var(--semantic-color-surface-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--semantic-color-text-secondary);
    font-style: italic;
  }
}

.section-divider {
  border: none;
  border-top: 1px solid var(--semantic-color-border-default);
  margin: var(--semantic-size-gap-lg) 0;
}
</style>