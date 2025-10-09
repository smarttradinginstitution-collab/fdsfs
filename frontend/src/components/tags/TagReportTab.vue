<template>
  <div class="tag-report-container">
    <div v-if="isLoading" class="loading-state">
      <LoadingSpinner />
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="stats.length === 0" class="empty-state">
      <p>No trading data found for the selected period.</p>
      <p>Assign some tags to your trades to see performance analytics here.</p>
    </div>
    <div v-else class="content">
      <BaseWidget class="chart-widget">
        <TagPerformanceChart :stats="stats" />
      </BaseWidget>
      <BaseTable :items="stats" :headers="headers">
        <template #tag_name="{ item }">
          <BasePill :style="{ backgroundColor: item.tag_color, color: getTextColor(item.tag_color) }">
            {{ item.tag_name }}
          </BasePill>
        </template>
        <template #total_pnl="{ item }">
          <span :class="item.total_pnl >= 0 ? 'text-positive' : 'text-negative'">
            {{ formatCurrency(item.total_pnl) }}
          </span>
        </template>
        <template #win_rate="{ item }">
          {{ formatPercentage(item.win_rate) }}
        </template>
        <template #avg_r_multiple="{ item }">
          {{ formatNumber(item.avg_r_multiple, 2) }} R
        </template>
      </BaseTable>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { useFilterStore } from '@/stores/filterStore';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BaseTable from '@/components/ui/BaseTable.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import TagPerformanceChart from '@/components/analytics/TagPerformanceChart.vue';
import { formatCurrency, formatPercentage, formatNumber } from '@/services/formatters';

const analyticsStore = useAnalyticsStore();
const filterStore = useFilterStore();
const tradingAccountsStore = useTradingAccountsStore();

const stats = computed(() => analyticsStore.tagPerformanceStats);
const isLoading = computed(() => analyticsStore.isLoading);
const error = computed(() => analyticsStore.error);

const headers = [
  { key: 'tag_name', text: 'Tag' },
  { key: 'total_pnl', text: 'Total P&L', align: 'right' },
  { key: 'win_rate', text: 'Win Rate', align: 'right' },
  { key: 'avg_r_multiple', text: 'Avg. R-Multiple', align: 'right' },
  { key: 'total_trades', text: 'Total Trades', align: 'right' },
];

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};

// Fetch data when the component mounts
onMounted(() => {
  analyticsStore.fetchTagPerformanceStats();
});

// Watch for changes in global filters and refetch data
watch(
  [() => filterStore.startDate, () => filterStore.endDate, () => tradingAccountsStore.selectedTradingAccount],
  () => {
    analyticsStore.fetchTagPerformanceStats();
  },
  { deep: true }
);
</script>

<style scoped>
.content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.chart-widget {
  padding: var(--semantic-size-inset-lg);
}
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 400px;
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}
.empty-state p:first-child {
  font-weight: 500;
  color: var(--semantic-color-text-primary);
}
.text-positive {
  color: var(--semantic-color-feedback-positive-text);
}
.text-negative {
  color: var(--semantic-color-feedback-negative-text);
}
</style>