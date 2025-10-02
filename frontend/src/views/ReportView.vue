<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import TradeStats from '@/components/trades/TradeStats.vue';
import { useTrade } from '@/composables/useTrade';
import { useTradeNavigation } from '@/composables/useTradeNavigation';

const route = useRoute();
const router = useRouter();
const { trade, isLoading, error, fetchTrade, markAsReviewed } = useTrade();

// State for the "Mark as reviewed" button
const isReviewed = computed(() => trade.value?.is_reviewed || false);
const isMarkingAsReviewed = ref(false);

const handleMarkAsReviewed = async () => {
  if (!trade.value || isReviewed.value) return;
  isMarkingAsReviewed.value = true;
  await markAsReviewed(trade.value.id);
  isMarkingAsReviewed.value = false;
};

// --- Navigation ---
const {
  isLoading: isNavLoading,
  fetchTradeList,
  getNavigationIds,
} = useTradeNavigation();

let navigation = ref({ prevTradeId: null, nextTradeId: null });

const goToPrevTrade = () => {
  if (navigation.value.prevTradeId) {
    router.push({ name: 'Report', params: { id: navigation.value.prevTradeId } });
  }
};

const goToNextTrade = () => {
  if (navigation.value.nextTradeId) {
    router.push({ name: 'Report', params: { id: navigation.value.nextTradeId } });
  }
};

// Tabs for the left column
const leftColumnTabs = [
  { name: 'stats', label: 'Stats' },
  { name: 'playbook', label: 'Playbook' },
  { name: 'executions', label: 'Executions' },
  { name: 'attachments', label: 'Attachments' },
];
const activeLeftTab = ref('stats');

// Tabs for the right column
const rightColumnTabs = [
  { name: 'trade-note', label: 'Trade note' },
  { name: 'daily-journal', label: 'Daily journal' },
];
const activeRightTab = ref('trade-note');

// Fetch trade data when the component mounts and when the route changes
onMounted(() => {
  fetchTrade(route.params.id);
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchTrade(newId);
  }
});

// When the main trade data loads, fetch the list of trades for navigation
watch(trade, (newTrade) => {
  if (newTrade && newTrade.trading_account_id) {
    // Dates can be passed here for more specific filtering if needed
    fetchTradeList(newTrade.trading_account_id, null, null).then(() => {
      navigation = getNavigationIds(newTrade.id);
    });
  }
});
</script>

<template>
  <div class="report-layout">
    <!-- Secondary Header -->
    <header class="secondary-header">
      <div class="navigation-controls">
        <button
          class="nav-button"
          :disabled="!navigation.prevTradeId || isNavLoading"
          @click="goToPrevTrade"
        >&lt;</button>
        <div v-if="trade" class="trade-identifier">
          <span class="asset-name">{{ trade.asset.name }}</span>
          <span class="trade-date">{{ trade.display_date }}</span>
        </div>
        <div v-else-if="isLoading" class="trade-identifier">
          <span class="asset-name">Loading...</span>
        </div>
        <button
          class="nav-button"
          :disabled="!navigation.nextTradeId || isNavLoading"
          @click="goToNextTrade"
        >&gt;</button>
      </div>
      <div class="action-buttons">
        <button
          class="action-button"
          :class="{ 'is-reviewed': isReviewed }"
          :disabled="isReviewed || isMarkingAsReviewed"
          @click="handleMarkAsReviewed"
        >
          <span v-if="isMarkingAsReviewed">Saving...</span>
          <span v-else-if="isReviewed">Reviewed ✓</span>
          <span v-else>Mark as reviewed</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Left Column: Details and Metrics -->
      <div class="left-column">
        <BaseTabs v-model="activeLeftTab" :tabs="leftColumnTabs" />
        <div class="tab-content">
          <div v-if="activeLeftTab === 'stats'">
            <div v-if="isLoading" class="loading-state">
              <p>Loading trade data...</p>
            </div>
            <div v-else-if="error" class="error-state">
              <p>Error: {{ error }}</p>
            </div>
            <TradeStats v-else-if="trade" :trade="trade" />
          </div>
          <div v-else-if="activeLeftTab === 'playbook'">
            <p>Playbook content will go here.</p>
          </div>
          <div v-else-if="activeLeftTab === 'executions'">
            <p>Executions content will go here.</p>
          </div>
          <div v-else-if="activeLeftTab === 'attachments'">
            <p>Attachments content will go here.</p>
          </div>
        </div>
      </div>

      <!-- Right Column: Notes Area -->
      <div class="right-column">
        <BaseTabs v-model="activeRightTab" :tabs="rightColumnTabs" />
        <div class="tab-content">
          <div v-if="activeRightTab === 'trade-note'">
            <div class="notes-placeholder">
              <p>Rich text editor for Trade Notes will be implemented here.</p>
            </div>
          </div>
          <div v-else-if="activeRightTab === 'daily-journal'">
            <div class="notes-placeholder">
              <p>Rich text editor for Daily Journal will be implemented here.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped>
.report-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--semantic-size-inset-lg);
  gap: var(--semantic-size-stack-lg);
}

.secondary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.navigation-controls {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
}

.trade-identifier {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.asset-name {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}

.trade-date {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.nav-button {
  // Placeholder styles
  background: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm);
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: var(--semantic-size-stack-sm);
}

.action-button {
  background: var(--semantic-color-interactive-secondary-default);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  font: var(--semantic-font-style-button-label-medium);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;

  &:hover:not(:disabled) {
    background-color: var(--semantic-color-interactive-secondary-hover);
  }

  &.is-reviewed {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
    border-color: var(--semantic-color-feedback-positive-text);
    cursor: default;
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.7;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 35fr 65fr; /* 35% and 65% split */
  gap: var(--semantic-size-stack-lg);
  flex-grow: 1;
}

.left-column,
.right-column {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-md);
  border: 1px solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
}

.tab-content {
  flex-grow: 1;
}

.notes-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--semantic-color-text-tertiary);
  font: var(--semantic-font-style-body-lg);
}
</style>