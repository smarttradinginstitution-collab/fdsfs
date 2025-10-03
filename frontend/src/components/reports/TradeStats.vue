<script setup>
import { computed } from 'vue';
import { formatCurrency, formatNumber } from '@/services/formatters.js';

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

  const addStat = (label, value, options = {}) => {
    if (value !== null && value !== undefined && value !== '') {
      stats.push({ label, value, ...options });
    }
  };

  addStat('Net P&L', formatCurrency(t.p_l), {
    style: t.p_l >= 0 ? 'pnl-positive' : 'pnl-negative',
    specialClass: 'net-pnl-stat'
  });

  addStat('Side', t.direction);

  const totalFees = (t.fees || 0) + (t.commissions || 0);
  addStat('Commissions & Fees', formatCurrency(totalFees * -1), { style: 'pnl-negative' });

  addStat('Net ROI', formatPercentage(t.net_roi), { style: t.net_roi >= 0 ? 'pnl-positive' : 'pnl-negative' });
  addStat('Gross P&L', formatCurrency(t.gross_p_l));

  addStat('Take Profit', formatCurrency(t.take_profit_price));
  addStat('Stop Loss', formatCurrency(t.stop_loss_price), { style: 'pnl-negative' });

  // MAE / MFE Logic
  if (t.highest_price_during_trade !== null && t.lowest_price_during_trade !== null) {
    const maeMfePayload = {
      isMaeMfe: true, // Special flag for unique rendering
      mae: { value: '', style: 'pnl-negative' },
      mfe: { value: '', style: 'pnl-positive' }
    };
    if (t.direction === 'LONG') {
      maeMfePayload.mae.value = formatCurrency(t.lowest_price_during_trade);
      maeMfePayload.mfe.value = formatCurrency(t.highest_price_during_trade);
    } else { // SHORT
      maeMfePayload.mae.value = formatCurrency(t.highest_price_during_trade);
      maeMfePayload.mfe.value = formatCurrency(t.lowest_price_during_trade);
    }
    addStat('MAE / MFE', '', maeMfePayload);
  }

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
    addStat('Entry Time', new Date(t.entry_timestamp).toLocaleTimeString('en-GB'));
  }
  if(t.exit_timestamp) {
    addStat('Exit Time', new Date(t.exit_timestamp).toLocaleTimeString('en-GB'));
  }

  addStat('Confluences', 'Select tag', { interactive: true });
  addStat('Entry Timeframe', 'Select Timeframe', { interactive: true });

  return stats;
});

</script>

<template>
  <div class="trade-stats-list">
    <div v-for="stat in displayStats" :key="stat.label" :class="['stat-item', stat.specialClass]">
      <span class="stat-label">{{ stat.label }}</span>

      <div v-if="stat.isMaeMfe" class="mae-mfe-values">
          <span :class="['stat-value', 'pill', stat.mae.style]">{{ stat.mae.value }}</span>
          <span :class="['stat-value', 'pill', stat.mfe.style]">{{ stat.mfe.value }}</span>
      </div>

      <span v-else :class="['stat-value', stat.style, { 'is-interactive': stat.interactive }]">
        {{ stat.value }}
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.trade-stats-list {
  display: flex;
  flex-direction: column;
}

.stat-item {
  display: grid;
  grid-template-columns: 40% 1fr;
  gap: var(--semantic-size-stack-md);
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);

  &.pnl-positive {
    color: var(--semantic-color-feedback-positive-text);
  }

  &.pnl-negative {
    color: var(--semantic-color-feedback-negative-text);
  }

  &.is-interactive {
    cursor: pointer;
    color: var(--semantic-color-text-interactive);
    &:hover {
      text-decoration: underline;
    }
  }
}

.mae-mfe-values {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}

.pill {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-tag);
  font: var(--semantic-font-style-label-sm);

  &.pnl-positive {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
  }

  &.pnl-negative {
    background-color: var(--semantic-color-feedback-negative-surface);
    color: var(--semantic-color-feedback-negative-text);
  }
}

// Special styling for the main Net P&L stat
.net-pnl-stat {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--semantic-size-stack-xxs);
  padding-bottom: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-sm);
  border-bottom: 1px solid var(--semantic-color-border-default);

  .stat-label {
    font: var(--semantic-font-style-label-md);
  }

  .stat-value {
    font: var(--semantic-font-style-metric-display);
  }
}
</style>