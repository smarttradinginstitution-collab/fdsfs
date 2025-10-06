<template>
  <BaseModal
    :show="isOpen"
    title="Create New Trade Note"
    @close="$emit('close')"
  >
    <div class="modal-content">
      <div class="link-trade-section">
        <button class="button-link-trade" @click="toggleTradeLink">
          <LinkIcon class="icon" />
          <span>{{ selectedTrade ? 'Change Linked Trade' : 'Link to a Trade' }}</span>
        </button>
        <div v-if="selectedTrade" class="linked-trade-info">
          <span>Linked to: {{ selectedTrade.asset?.symbol ?? 'N/A' }} on {{ new Date(selectedTrade.entry_timestamp).toLocaleDateString() }}</span>
          <button @click="clearSelectedTrade" class="clear-button">
            <XMarkIcon class="icon" />
          </button>
        </div>
      </div>

      <!-- Recent Trades Table -->
      <div v-if="showTrades" class="recent-trades-container">
        <div v-if="store.isLoadingTrades">Loading trades...</div>
        <div v-else-if="store.error">{{ store.error }}</div>
        <table v-else-if="store.recentTrades.length > 0" class="trades-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Entry Date</th>
              <th>Net P&L</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="trade in store.recentTrades"
              :key="trade.id"
              @click="selectTrade(trade)"
              class="trade-row"
              :class="{
                'is-selected': selectedTrade && selectedTrade.id === trade.id,
                'is-linked': trade.note_id,
              }"
            >
              <td>{{ trade.asset?.symbol ?? 'N/A' }}</td>
              <td>{{ new Date(trade.entry_timestamp).toLocaleDateString() }}</td>
              <td>{{ formatCurrency(trade.p_l) }}</td>
              <td class="action-cell">
                <div v-if="trade.note_id" class="linked-icon-container">
                  <SolidLinkIcon class="linked-icon" />
                </div>
                <BaseButton v-else variant="secondary" size="small">Link</BaseButton>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else>No recent trades found.</div>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="$emit('close')">Cancel</BaseButton>
      <BaseButton variant="primary" @click="handleSave">Save</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseModal from '../ui/BaseModal.vue';
import BaseButton from '../ui/BaseButton.vue';
import { LinkIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { LinkIcon as SolidLinkIcon } from '@heroicons/vue/24/solid';
import { formatCurrency } from '../../services/formatters';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'create']);

const store = useNotebookStore();
const selectedTrade = ref(null);
const showTrades = ref(false);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    store.fetchRecentTrades();
    selectedTrade.value = null;
    showTrades.value = false;
  }
});

const toggleTradeLink = () => {
  showTrades.value = !showTrades.value;
};

const selectTrade = (trade) => {
  if (trade.note_id) return; // Prevent selecting already linked trades
  selectedTrade.value = trade;
  showTrades.value = false; // Hide table after selection
};

const clearSelectedTrade = () => {
  selectedTrade.value = null;
};

const handleSave = () => {
  let title = '';
  const tradeId = selectedTrade.value ? selectedTrade.value.id : null;

  if (tradeId && selectedTrade.value) {
    const tradeDate = new Date(selectedTrade.value.entry_timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    const symbol = selectedTrade.value.asset?.symbol ?? 'N/A';
    title = `${symbol} : ${tradeDate}`;
  } else {
    const today = new Date().toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
    });
    title = `Trade Notes for ${today}`;
  }

  emit('create', { title, tradeId });
  emit('close');
};
</script>

<style lang="scss" scoped>
.modal-content {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-lg);
}

.button-link-trade {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--base-size-spacing-2);
  font: var(--semantic-font-style-button-label-medium);
  padding-block: var(--semantic-size-button-padding-block-medium);
  padding-inline: var(--semantic-size-button-padding-inline-medium);
  border-radius: var(--semantic-border-radius-interactive);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-interactive);
  cursor: pointer;
  transition: all var(--base-animation-duration-fast);

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
    border-color: var(--semantic-color-border-subtle);
  }
}

.link-trade-section {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-md);

  .icon {
    width: 1rem;
    height: 1rem;
    margin-right: var(--semantic-size-inset-xs);
  }
}

.linked-trade-info {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-pill);
}

.clear-button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--semantic-color-text-tertiary);
  padding: 0;
  display: flex;
  align-items: center;
  &:hover {
    color: var(--semantic-color-text-danger);
  }
}

.recent-trades-container {
  margin-top: var(--semantic-size-inset-sm);
  border-top: 1px solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-inset-lg);
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
  font: var(--semantic-font-style-body-sm);

  th,
  td {
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-xs);
    text-align: left;
    border-bottom: 1px solid var(--semantic-color-border-default);
  }

  th {
    color: var(--semantic-color-text-secondary);
    font-weight: 600;
  }

  .action-cell {
    text-align: center;
  }

  .trade-row {
    cursor: pointer;
    transition: background-color 0.2s ease;
    &:hover {
      background-color: var(--semantic-color-surface-secondary);
    }
    &.is-selected {
      background-color: var(--semantic-color-surface-selected);
    }
    &.is-linked {
      cursor: not-allowed;
      opacity: 0.6;
      &:hover {
        background-color: transparent;
      }
    }
  }
}

.linked-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--semantic-color-text-success);
}
</style>