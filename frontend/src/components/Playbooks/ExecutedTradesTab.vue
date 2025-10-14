<template>
  <div class="executed-trades-tab">
    <div v-if="tradesStore.isLoading" class="loading-state">
      <p>Loading trades...</p>
    </div>
    <div v-else-if="executedTrades.length === 0" class="empty-state">
      <p>No trades have been executed for this playbook yet.</p>
    </div>
    <div v-else class="table-container">
      <table class="trades-table">
        <thead>
          <tr>
            <th>Open Date</th>
            <th>Symbol</th>
            <th>Status</th>
            <th>Close Date</th>
            <th>Entry Price</th>
            <th>Exit Price</th>
            <th>Net P&L</th>
            <th>Net ROI</th>
            <th>Setups</th>
            <th>Account Name</th>
            <th></th> <!-- For delete icon -->
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in paginatedTrades" :key="trade.id">
            <td>{{ formatDate(trade.entry_timestamp) }}</td>
            <td>{{ trade.symbol_snapshot }}</td>
            <td>
              <span :class="getStatusClass(trade.p_l)">
                {{ trade.p_l >= 0 ? 'WIN' : 'LOSS' }}
              </span>
            </td>
            <td>{{ formatDate(trade.exit_timestamp) }}</td>
            <td>{{ formatCurrency(trade.entry_price) }}</td>
            <td>{{ formatCurrency(trade.exit_price) }}</td>
            <td :class="trade.p_l >= 0 ? 'positive' : 'negative'">{{ formatCurrency(trade.p_l) }}</td>
            <td :class="trade.net_roi >= 0 ? 'positive' : 'negative'">{{ formatPercentage(trade.net_roi) }}</td>
            <td>-</td> <!-- Placeholder for Setups -->
            <td>{{ trade.trading_account_name }}</td>
            <td>
              <button class="delete-btn" @click="promptDelete(trade)">
                <TrashIcon />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination-footer">
        <span>Result: 1 - {{ paginatedTrades.length }} of {{ executedTrades.length }} trades</span>
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1">&lt;</button>
          <span>{{ currentPage }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages">&gt;</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmationModal
      :show="isDeleteModalVisible"
      title="Delete Trade"
      :message="`Are you sure you want to delete this trade for ${tradeToDelete?.symbol_snapshot}? This action cannot be undone.`"
      @close="isDeleteModalVisible = false"
      @confirm="handleConfirmDelete"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useTradesStore } from '@/stores/trades';
import { formatCurrency, formatPercentage } from '@/services/formatters.js';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';

const route = useRoute();
const tradesStore = useTradesStore();

const playbookId = computed(() => route.params.id);

onMounted(() => {
  if (playbookId.value) {
    tradesStore.fetchTradesByPlaybook(playbookId.value);
  }
});

const executedTrades = computed(() => tradesStore.playbookTrades);

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleDateString('en-US', {
    year: '2-digit',
    month: '2-digit',
    day: '2-digit',
  });
};

const getStatusClass = (pnl) => {
  if (pnl > 0) return 'status-win';
  if (pnl < 0) return 'status-loss';
  return 'status-breakeven';
};

// --- Delete Logic ---
const isDeleteModalVisible = ref(false);
const tradeToDelete = ref(null);

const promptDelete = (trade) => {
  tradeToDelete.value = trade;
  isDeleteModalVisible.value = true;
};

const handleConfirmDelete = async () => {
  if (tradeToDelete.value) {
    await tradesStore.deleteTrade(tradeToDelete.value.id);
  }
  isDeleteModalVisible.value = false;
  tradeToDelete.value = null;
};

// --- Pagination Logic ---
const currentPage = ref(1);
const itemsPerPage = ref(10); // Or any number that fits the design

const totalPages = computed(() => {
  return Math.ceil(executedTrades.value.length / itemsPerPage.value);
});

const paginatedTrades = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return executedTrades.value.slice(start, end);
});

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};
</script>

<style scoped>
.table-container {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  overflow: hidden; /* To keep the border radius on the table */
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
}

.trades-table th,
.trades-table td {
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-lg);
  text-align: left;
  border-bottom: 1px solid var(--semantic-color-border-default);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
}

.trades-table th {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase;
}

.trades-table tbody tr:last-child td {
  border-bottom: none;
}

.status-win, .status-loss {
  padding: 0.25rem 0.5rem;
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-label-sm);
  text-transform: uppercase;
}

.status-win {
  background-color: var(--semantic-color-success-surface-default);
  color: var(--semantic-color-success-text-default);
}

.status-loss {
  background-color: var(--semantic-color-danger-surface-default);
  color: var(--semantic-color-danger-text-default);
}

.positive {
  color: var(--semantic-color-success-text-default);
}

.negative {
  color: var(--semantic-color-danger-text-default);
}

.delete-btn {
  background: none;
  border: none;
  color: var(--semantic-color-danger-text-default);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state, .empty-state {
  padding: 4rem;
  text-align: center;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-lg);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  border-top: 1px solid var(--semantic-color-border-default);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.pagination-controls button {
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--semantic-color-text-primary);
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>