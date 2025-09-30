<template>
  <div class="rule-row">
    <div class="col-rule">
      <span class="drag-handle drag-handle-rule">&#x2630;</span>
      <span class="rule-text">{{ rule.rule }}</span>
    </div>
    <div class="col-metric">{{ formatPercentage(rule.metrics.follow_rate) }}</div>
    <div class="col-metric">{{ formatCurrency(rule.metrics.net_pnl) }}</div>
    <div class="col-metric">{{ formatProfitFactor(rule.metrics.profit_factor) }}</div>
    <div class="col-metric">{{ formatPercentage(rule.metrics.win_rate) }}</div>
    <div class="col-action">
      <button class="kebab-menu">...</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import { formatCurrency, formatPercentage, formatNumber } from '@/services/formatters.js';

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
});

const formatProfitFactor = (value) => {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return formatNumber(value, 2);
};
</script>

<style scoped>
.rule-row {
  display: grid;
  grid-template-columns: minmax(0, 3fr) repeat(4, minmax(0, 1fr)) 40px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem var(--semantic-size-inset-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
  font: var(--semantic-font-style-body-lg);
}

.rule-row:last-child {
  border-bottom: none;
}

.col-rule {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--semantic-color-text-primary);
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
}

.col-metric {
  text-align: right;
  color: var(--semantic-color-text-primary);
}

.col-action {
  text-align: center;
}

.kebab-menu {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  color: var(--semantic-color-text-secondary);
}
</style>