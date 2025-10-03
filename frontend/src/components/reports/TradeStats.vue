<script setup>
import { computed } from 'vue';
import { formatCurrency, formatNumber, formatPercentage } from '@/services/formatters.js';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const displayStats = computed(() => {
  if (!props.trade) return [];

  const t = props.trade;
  const stats = [];

  // Helper function to add a stat only if its value is valid
  const addStat = (label, value, options = {}) => {
    if (value !== null && value !== undefined) {
      stats.push({ label, value, ...options });
    }
  };

  addStat('Net P&L', formatCurrency(t.p_l), { style: t.p_l >= 0 ? 'pnl-positive' : 'pnl-negative' });
  addStat('Side', t.direction);
  addStat('Commissions & Fees', formatCurrency(t.fees + t.commissions), { style: 'pnl-negative' });
  addStat('Net ROI', formatPercentage(t.net_roi), { style: t.net_roi >= 0 ? 'pnl-positive' : 'pnl-negative' });
  addStat('Gross P&L', formatCurrency(t.gross_p_l));

  if (t.playbook) {
    addStat('Playbook', t.playbook.title);
  } else {
     addStat('Playbook', 'Select Playbook', { interactive: true });
  }

  addStat('Trade Risk', formatCurrency(t.trade_risk), { style: 'pnl-negative' });
  addStat('Realized R-Multiple', `${formatNumber(t.r_multiple, 2)} R`, { style: t.r_multiple >= 0 ? 'pnl-positive' : 'pnl-negative' });

  addStat('Average Entry', formatCurrency(t.entry_price));
  addStat('Average Exit', formatCurrency(t.exit_price));

  if(t.entry_timestamp) {
    addStat('Entry Time', new Date(t.entry_timestamp).toLocaleTimeString());
  }
  if(t.exit_timestamp) {
    addStat('Exit Time', new Date(t.exit_timestamp).toLocaleTimeString());
  }

  addStat('Confluences', 'Select tag', { interactive: true });
  addStat('Entry Timeframe', 'Select Timeframe', { interactive: true });


  return stats;
});

</script>

<template>
  <div class="trade-stats-list">
    <div v-for="stat in displayStats" :key="stat.label" class="stat-item">
      <span class="stat-label">{{ stat.label }}</span>
      <span :class="['stat-value', stat.style, { 'is-interactive': stat.interactive }]">
        {{ stat.value }}
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.trade-stats-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-md);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
}

.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font: var(--semantic-font-style-body-sm-bold);
  color: var(--semantic-color-text-primary);

  &.pnl-positive {
    color: var(--semantic-color-text-success-strong);
  }

  &.pnl-negative {
    color: var(--semantic-color-text-danger-strong);
  }

  &.is-interactive {
    cursor: pointer;
    color: var(--semantic-color-text-interactive-default);
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>