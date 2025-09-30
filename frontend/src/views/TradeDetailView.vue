<script setup>
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useTradesStore } from '@/stores/trades';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const route = useRoute();
const tradesStore = useTradesStore();

const trade = computed(() => tradesStore.selectedTrade);
const isLoading = computed(() => tradesStore.isLoading);

onMounted(() => {
  const tradeId = route.params.id;
  if (tradeId) {
    tradesStore.fetchTradeById(tradeId);
  }
});
</script>

<template>
  <div class="trade-detail-view">
    <LoadingSpinner v-if="isLoading" />
    <div v-else-if="trade">
      <h1 class="view-title">Trade: {{ trade.symbol }}</h1>
      <BaseWidget>
        <div class="trade-details-grid">
          <div><strong>Side:</strong> {{ trade.direction }}</div>
          <div><strong>Net P&L:</strong> {{ trade.p_l }}</div>
          <div><strong>Date:</strong> {{ new Date(trade.entry_timestamp).toLocaleDateString() }}</div>
          <div><strong>Playbook:</strong> {{ trade.playbook?.title || 'N/A' }}</div>
          <div><strong>Entry Price:</strong> {{ trade.entry_price }}</div>
          <div><strong>Exit Price:</strong> {{ trade.exit_price }}</div>
          <div><strong>Position Size:</strong> {{ trade.position_size }}</div>
        </div>
      </BaseWidget>
    </div>
    <div v-else>
      <h1 class="view-title">Trade Not Found</h1>
      <p>The requested trade could not be found.</p>
    </div>
  </div>
</template>

<style scoped>
.trade-detail-view {
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.view-title {
  font: var(--semantic-font-style-heading-h3);
  color: var(--semantic-color-text-primary);
}
.trade-details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--semantic-size-stack-lg);
}
</style>