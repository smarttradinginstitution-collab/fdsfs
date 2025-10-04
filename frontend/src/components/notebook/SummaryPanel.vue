<template>
  <div class="summary-panel">
    <button @click="isExpanded = !isExpanded" class="panel-header">
      <div class="header-title">
        <IconChevronRight class="chevron-icon" :class="{ 'is-rotated': isExpanded }" />
        <h3 class="title">Net P&L: {{ formatCurrency(stats?.net_pnl) }}</h3>
      </div>
    </button>

    <div v-if="isExpanded" class="panel-content">
      <div v-if="isLoading" class="loading-state">Loading stats...</div>
      <div v-else-if="error" class="error-state">{{ error }}</div>
      <div v-else-if="stats" class="stats-grid">
        <StatItem label="Total Trades" :value="stats.trade_count" />
        <StatItem label="Winners" :value="stats.winning_trades" />
        <StatItem label="Gross P&L" :value="formatCurrency(stats.gross_profit)" />
        <StatItem label="Commissions" :value="formatCurrency(stats.gross_loss)" />
        <StatItem label="Winrate" :value="formatPercentage(stats.win_rate)" />
        <StatItem label="Losers" :value="stats.losing_trades" />
        <StatItem label="Volume" :value="0" /> <!-- Placeholder -->
        <StatItem label="Profit Factor" :value="stats.profit_factor" />
      </div>
       <div v-else class="empty-state">No Closed NET P&L on this day</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import api from '@/services/api';
import { formatCurrency, formatPercentage } from '@/services/formatters';

import IconChevronRight from '@/components/icons/ArrowRightIcon.vue';
import StatItem from '@/components/notebook/StatItem.vue';

const props = defineProps({
  note: {
    type: Object,
    required: true,
  },
});

const isExpanded = ref(false);
const stats = ref(null);
const isLoading = ref(false);
const error = ref(null);

const accountsStore = useTradingAccountsStore();

const fetchStats = async () => {
  if (!props.note || !accountsStore.selectedAccount) {
    stats.value = null;
    return;
  }

  isLoading.value = true;
  error.value = null;
  stats.value = null;

  try {
    const noteDate = new Date(props.note.created_at).toISOString().split('T')[0];
    const accountId = accountsStore.selectedAccount.id;

    const response = await api.get(`/trades/performance/metrics/${accountId}`, {
      params: {
        start_date: noteDate,
        end_date: noteDate,
      },
    });

    if (response.data && response.data.stats) {
      stats.value = response.data.stats;
    } else {
        // Handle case where API returns success but no stats
        stats.value = null;
    }
  } catch (err) {
    console.error("Failed to fetch summary stats:", err);
    error.value = "Could not load performance data.";
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.note.id, fetchStats, { immediate: true });
onMounted(fetchStats);

</script>

<style lang="scss" scoped>
.summary-panel {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  background-color: var(--semantic-color-surface-secondary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: var(--fluid-spacing-m);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  color: var(--semantic-color-text-primary);
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-s);

  .chevron-icon {
    width: 20px;
    height: 20px;
    transition: transform 0.2s ease-in-out;
    &.is-rotated {
      transform: rotate(90deg);
    }
  }

  .title {
    font-size: var(--fluid-font-size-l);
    font-weight: 600;
    margin: 0;
  }
}

.panel-content {
  padding: var(--fluid-spacing-m);
  border-top: 1px solid var(--semantic-color-border-default);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--fluid-spacing-l);
}

.loading-state, .error-state, .empty-state {
    color: var(--semantic-color-text-secondary);
    font-style: italic;
}
</style>