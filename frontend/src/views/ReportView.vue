<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import TradeStats from '@/components/reports/TradeStats.vue';
import PillTabs from '@/components/ui/PillTabs.vue';
import RichTextEditor from '@/components/ui/RichTextEditor.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import IconButton from '@/components/ui/IconButton.vue';
import PencilIcon from '@/components/icons/PencilIcon.vue';
import EditTradeDetailsModal from '@/components/reports/EditTradeDetailsModal.vue';
import { useTradesStore } from '@/stores/trades';

// --- STATE ---
const route = useRoute();
const router = useRouter();
const tradesStore = useTradesStore();

const activeTab = ref('stats');
const rightColumnActiveTab = ref('trade-note');
const isEditModalOpen = ref(false);

const leftColumnTabs = [
  { id: 'stats', label: 'Stats' },
  { id: 'playbook', label: 'Playbook' },
  { id: 'executions', label: 'Executions' },
  { id: 'attachments', label: 'Attachments' },
];

const rightColumnTabs = [
  { id: 'trade-note', label: 'Trade note' },
  { id: 'daily-journal', label: 'Daily journal' },
];

// --- COMPUTED ---
const trade = computed(() => tradesStore.selectedTrade);
const isLoading = computed(() => tradesStore.isTradeLoading);
const error = ref(null); // Potremmo collegarlo a uno stato di errore dello store

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
  if (prevId) {
    router.push({ name: 'report-detail', params: { id: prevId } });
  }
};

const handleNext = () => {
  const nextId = tradesStore.getNextTradeId;
  if (nextId) {
    router.push({ name: 'report-detail', params: { id: nextId } });
  }
};

const openEditModal = () => {
  isEditModalOpen.value = true;
};

const handleUpdateTradeDetails = (payload) => {
  if (trade.value) {
    tradesStore.updateTrade(trade.value.id, payload);
  }
};

const editableNotes = ref('');
watch(trade, (newTrade) => {
  if (newTrade) {
    editableNotes.value = newTrade.notes || '';
  }
}, { immediate: true });

const handleSaveNotes = () => {
  if (trade.value) {
    tradesStore.updateTrade(trade.value.id, { notes: editableNotes.value });
  }
};

const fetchRequiredData = async (id) => {
  // Assicurati che l'elenco completo dei trade sia caricato per la navigazione
  if (tradesStore.trades.length === 0) {
    await tradesStore.fetchTrades();
  }
  await tradesStore.fetchTradeById(id);
};

// --- LIFECYCLE & WATCHERS ---
onMounted(() => {
  fetchRequiredData(route.params.id);
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchRequiredData(newId);
  }
});

</script>

<template>
  <div class="report-detail-view">
    <div v-if="isLoading" class="loading-state">
      <p>Loading trade details...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="trade" class="report-container">
      <!-- Secondary Header -->
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

      <!-- Main Content -->
      <main class="report-content">
        <!-- Left Column -->
        <div class="left-column">
          <BaseWidget class="stats-widget">
          <div class="stats-header">
            <h3>Statistics</h3>
            <IconButton @click="openEditModal" class="edit-button" aria-label="Edit Trade Details">
              <PencilIcon />
            </IconButton>
          </div>
            <BaseTabs v-model="activeTab" :tabs="leftColumnTabs">
              <template #stats>
                <TradeStats :trade="trade" />
            </template>
            <template #playbook>
              <div>Contenuto Playbook</div>
            </template>
            <template #executions>
              <div>Contenuto Executions</div>
            </template>
            <template #attachments>
              <div>Contenuto Attachments</div>
            </template>
          </BaseTabs>
          </BaseWidget>
        </div>

        <!-- Right Column -->
        <div class="right-column">
        <BaseWidget class="notes-widget">
          <div class="right-column-content">
            <div class="notes-header">
              <PillTabs v-model="rightColumnActiveTab" :tabs="rightColumnTabs" />
              <BaseButton @click="handleSaveNotes" size="small" variant="primary">Save Notes</BaseButton>
            </div>
            <div v-if="rightColumnActiveTab === 'trade-note'" class="editor-container">
              <RichTextEditor v-model="editableNotes" />
            </div>
            <div v-if="rightColumnActiveTab === 'daily-journal'">
              <p>Daily Journal content to be implemented.</p>
            </div>
            </div>
        </BaseWidget>
        </div>
      </main>
    </div>
    <div v-else class="empty-state">
      <p>Trade not found.</p>
    </div>

    <EditTradeDetailsModal
      v-if="trade"
      v-model="isEditModalOpen"
      :trade="trade"
      @save="handleUpdateTradeDetails"
    />
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
  border-bottom: 1px solid var(--semantic-color-border-default);
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

// Stili per i pulsanti di azione, in attesa di un eventuale componente base
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
  min-height: 0; // Fix per flexbox in contenitori scrollabili
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.left-column {
  flex: 0 0 33%;
}

.right-column {
  flex: 1;
}

.stats-widget,
.notes-widget {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  // Override BaseWidget's default padding if it has any
  // This lets our internal layout control the spacing.
  padding: var(--semantic-size-inset-lg);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-stack-sm);

  h3 {
    font: var(--semantic-font-style-heading-md);
    color: var(--semantic-color-text-primary);
  }
}

.right-column-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-lg);
  flex-grow: 1;
}

.notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
</style>