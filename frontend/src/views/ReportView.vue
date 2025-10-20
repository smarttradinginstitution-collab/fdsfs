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
import { useLoadingStore } from '@/stores/loadingStore';
import { useNotebookStore } from '@/stores/notebookStore';
import { storeToRefs } from 'pinia';

// --- STATE ---
const route = useRoute();
const router = useRouter();
const tradesStore = useTradesStore();
const imageStore = useImageStore();
const loadingStore = useLoadingStore();
const notebookStore = useNotebookStore();
const activeTab = ref('stats');
const isEditModalOpen = ref(false);
const isMetadataModalOpen = ref(false);
const selectedImageForEdit = ref(null);
const tradeNote = ref(null);
const tradeDataCache = ref({});
const isNoteLoading = ref(true);

// Lightbox state
const isLightboxOpen = ref(false);
const lightboxCurrentIndex = ref(0);

const leftColumnTabs = [
  { id: 'stats', label: 'Stats' },
  { id: 'playbook', label: 'Playbook' },
  { id: 'executions', label: 'Executions' },
  { id: 'attachments', label: 'Attachments' },
];

// --- COMPUTED ---
const trade = computed(() => tradesStore.selectedTrade);
const { imagesForCurrentTrade } = storeToRefs(imageStore);

const primaryBeforeImage = computed(() => {
  if (!imagesForCurrentTrade.value || typeof imagesForCurrentTrade.value.find !== 'function') return null;
  return imagesForCurrentTrade.value.find(img => img.is_primary_before)
});
const primaryAfterImage = computed(() => {
  if (!imagesForCurrentTrade.value || typeof imagesForCurrentTrade.value.find !== 'function') return null;
  return imagesForCurrentTrade.value.find(img => img.is_primary_after)
});
const error = ref(null);

const tradeDate = computed(() => {
  if (!trade.value?.entry_timestamp) return '';
  const date = new Date(trade.value.entry_timestamp);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
});

// --- METHODS ---
const handlePrevious = () => {
  const prevId = tradesStore.getPreviousTradeId;
  if (prevId) router.push({ name: 'report-detail', params: { id: prevId } });
};

const handleNext = () => {
  const nextId = tradesStore.getNextTradeId;
  if (nextId) router.push({ name: 'report-detail', params: { id: nextId } });
};

const openEditModal = () => {
  isEditModalOpen.value = true;
};

const handleEditImage = (image) => {
  selectedImageForEdit.value = image;
  isMetadataModalOpen.value = true;
};

const handleUpdateTradeDetails = async (payload) => {
  if (trade.value) {
    await tradesStore.updateTrade(trade.value.id, payload);
    await tradesStore.fetchAllDataForDashboard();
  }
};

const openLightbox = (index) => {
  lightboxCurrentIndex.value = index;
  isLightboxOpen.value = true;
};

const closeLightbox = () => {
  isLightboxOpen.value = false;
};

const nextImage = () => {
  lightboxCurrentIndex.value = (lightboxCurrentIndex.value + 1) % imagesForCurrentTrade.value.length;
};

const prevImage = () => {
  lightboxCurrentIndex.value = (lightboxCurrentIndex.value - 1 + imagesForCurrentTrade.value.length) % imagesForCurrentTrade.value.length;
};

const selectTradeFromStore = async (tradeId) => {
  isNoteLoading.value = true;
  const cachedData = tradeDataCache.value[tradeId];

  if (cachedData && cachedData.trade && cachedData.trade.id) {
    tradesStore.selectedTrade = cachedData.trade;
    imageStore.imagesForCurrentTrade = cachedData.images || [];
    tradeNote.value = cachedData.note;
    if (cachedData.note) {
      notebookStore.selectNote(cachedData.note.id);
    } else {
      notebookStore.deselectNote();
    }
    isNoteLoading.value = false;

    // Start pre-fetching for next/prev from cache hit
    const prevId = tradesStore.getPreviousTradeId;
    const nextId = tradesStore.getNextTradeId;
    if (prevId) prefetchTradeData(prevId);
    if (nextId) prefetchTradeData(nextId);

    return;
  }

  const tradeInList = tradesStore.trades.find(t => t.id === tradeId);
  if (!tradeInList) {
    loadingStore.startLoading();
  }

  error.value = null;
  try {
    const [tradeDetails, images, note] = await Promise.all([
      tradeInList ? Promise.resolve(tradeInList) : tradesStore.fetchTradeById(tradeId),
      imageStore.fetchImagesForTrade(tradeId),
      notebookStore.fetchNoteByTradeId(tradeId).catch(() => null)
    ]);

    tradesStore.selectedTrade = tradeDetails;
    imageStore.imagesForCurrentTrade = images || [];
    tradeNote.value = note;

    if (note) {
      notebookStore.selectNote(note.id);
    } else {
      notebookStore.deselectNote();
    }

    // Populate cache
    if (tradeDetails && tradeDetails.id) {
      tradeDataCache.value[tradeId] = {
        trade: tradeDetails,
        images: images || [],
        note: note || null,
      };
    }

    // Pre-fetch next and previous trades
    const prevId = tradesStore.getPreviousTradeId;
    const nextId = tradesStore.getNextTradeId;
    if (prevId) prefetchTradeData(prevId);
    if (nextId) prefetchTradeData(nextId);

  } catch (e) {
    console.error("Error loading trade data:", e);
    error.value = "Failed to load trade data.";
    tradesStore.selectedTrade = null;
  } finally {
    loadingStore.stopLoading();
    isNoteLoading.value = false;
  }
};

const prefetchTradeData = async (tradeId) => {
  if (!tradeId || tradeDataCache.value[tradeId]) return;

  try {
    const [tradeDetails, images, note] = await Promise.all([
      tradesStore.fetchTradeById(tradeId),
      imageStore.fetchImagesForTrade(tradeId),
      notebookStore.fetchNoteByTradeId(tradeId).catch(() => null)
    ]);

    if (tradeDetails && tradeDetails.id) {
      tradeDataCache.value[tradeId] = {
        trade: tradeDetails,
        images: images || [],
        note: note || null,
      };
      console.log(`Prefetched and cached data for trade ${tradeId}`);
    }
  } catch (error) {
    console.warn(`Failed to prefetch data for trade ${tradeId}:`, error);
  }
};

// --- LIFECYCLE & WATCHERS ---
watch(() => route.params.id, (newId) => {
  if (newId) {
    selectTradeFromStore(newId);
  }
});

onMounted(() => {
  selectTradeFromStore(route.params.id);
});
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
            <TradeNoteEditor :initial-note="tradeNote" :trade-details="trade" :is-loading="isNoteLoading" />
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
    <ImageLightbox v-if="imagesForCurrentTrade && imagesForCurrentTrade.length > 0" :images="imagesForCurrentTrade" :current-index="lightboxCurrentIndex" :show="isLightboxOpen" @close="closeLightbox" @next="nextImage" @prev="prevImage" />
  </div>
</template>

<style lang="scss" scoped>
/* Stili invariati... */
</style>
