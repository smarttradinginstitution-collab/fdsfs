<template>
  <div class="combo-card" :class="cardTypeClass">
    <h3 class="card-title">{{ title }}</h3>
    <p class="prescriptive-text">{{ prescriptiveText }}</p>

    <div class="combo-elements">
      <div v-for="(element, index) in combo.combo.elements" :key="index" class="element-group">
        <BasePill :style="{ backgroundColor: element.item.color, color: getTextColor(element.item.color) }">
          {{ element.item.name }}
        </BasePill>
        <span v-if="index < combo.combo.elements.length - 1" class="plus-icon">+</span>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-item">
        <span class="metric-value">{{ combo.metrics.trade_count }}</span>
        <span class="metric-label">Trades</span>
      </div>
      <div class="metric-item">
        <span class="metric-value">{{ combo.metrics.win_rate_percent }}%</span>
        <span class="metric-label">Win Rate</span>
      </div>
      <div class="metric-item">
        <span class="metric-value">{{ combo.metrics.average_r_multiple }}R</span>
        <span class="metric-label">Avg. R-Multiple</span>
      </div>
      <div class="metric-item">
        <span class="metric-value">
          {{ formatCurrency(combo.metrics.total_pnl) }}
        </span>
        <span class="metric-label">Total P&L</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import BasePill from '@/components/ui/BasePill.vue';
import { formatCurrency } from '@/services/formatters';

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  combo: {
    type: Object,
    required: true,
  },
  type: {
    type: String,
    default: 'golden', // 'golden' or 'toxic'
  },
});

const cardTypeClass = computed(() => {
  return props.type === 'golden' ? 'is-golden' : 'is-toxic';
});

const prescriptiveText = computed(() => {
  return props.type === 'golden'
    ? 'You are at your best when...'
    : 'You struggle the most when...';
});

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};
</script>

<style scoped>
.combo-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  border: 1px solid var(--semantic-color-border-default);
  border-left-width: 4px;
}

.combo-card.is-golden {
  border-left-color: var(--semantic-color-border-success);
}

.combo-card.is-toxic {
  border-left-color: var(--semantic-color-border-danger);
}

.card-title {
  font: var(--semantic-font-style-heading-lg);
  margin-bottom: var(--semantic-size-stack-xxs);
}

.prescriptive-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-md);
}

.combo-elements {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  margin-bottom: var(--semantic-size-stack-lg);
}

.element-group {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.plus-icon {
  color: var(--semantic-color-text-disabled);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--semantic-size-stack-md);
}

.metric-item {
  display: flex;
  flex-direction: column;
}

.metric-value {
  font: var(--semantic-font-style-heading-xl);
}

.metric-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}
</style>