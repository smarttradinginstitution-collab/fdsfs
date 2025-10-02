<script setup>
import { computed } from 'vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

// Helper to format currency values
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

// Helper to format percentage values
const formatPercentage = (value) => {
  if (value === null || value === undefined) return '0.00%';
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

// Computed properties for styled data
const netPnl = computed(() => ({
  value: formatCurrency(props.trade.net_pnl),
  class: props.trade.net_pnl >= 0 ? 'is-positive' : 'is-negative',
}));

const commissions = computed(() => ({
  value: formatCurrency(props.trade.commissions_fees),
  class: 'is-negative',
}));

const tradeRisk = computed(() => ({
  value: formatCurrency(props.trade.trade_risk),
  class: 'is-negative',
}));

const realizedR = computed(() => ({
  value: `${props.trade.realized_r_multiple}R`,
  class: 'is-positive',
}));

const maetMfetTotal = computed(() => props.trade.maet + props.trade.mfet);
const maetWidth = computed(() => (props.trade.maet / maetMfetTotal.value) * 100);
const mfetWidth = computed(() => (props.trade.mfet / maetMfetTotal.value) * 100);

</script>

<template>
  <div class="stats-grid">
    <!-- Net P&L -->
    <div class="stat-item large-value">
      <span class="stat-label">Net P&L</span>
      <span class="stat-value" :class="netPnl.class">{{ netPnl.value }}</span>
    </div>

    <!-- Side -->
    <div class="stat-item">
      <span class="stat-label">Side</span>
      <span class="stat-value">{{ trade.side }}</span>
    </div>

    <!-- Fills -->
    <div class="stat-item">
      <span class="stat-label">Fills</span>
      <span class="stat-value">{{ trade.fills }}</span>
    </div>

    <!-- Firms Traded -->
    <div class="stat-item">
      <span class="stat-label">Firms traded</span>
      <span class="stat-value">{{ trade.firms_traded }}</span>
    </div>

    <!-- Return Per Pip -->
    <div class="stat-item">
      <span class="stat-label">Return Per Pip</span>
      <span class="stat-value">{{ formatCurrency(trade.return_per_pip) }}</span>
    </div>

    <!-- Pips -->
    <div class="stat-item">
      <span class="stat-label">Pips</span>
      <span class="stat-value">{{ trade.pips }}</span>
    </div>

    <!-- Commissions & Fees -->
    <div class="stat-item">
      <span class="stat-label">Commissions & Fees</span>
      <span class="stat-value" :class="commissions.class">{{ commissions.value }}</span>
    </div>

    <!-- Total Swap -->
    <div class="stat-item">
      <span class="stat-label">Total Swap</span>
      <span class="stat-value">{{ formatCurrency(trade.total_swap) }}</span>
    </div>

    <!-- Net ROI -->
    <div class="stat-item">
      <span class="stat-label">Net ROI</span>
      <span class="stat-value">{{ formatPercentage(trade.net_roi) }}</span>
    </div>

    <!-- Gross P&L -->
    <div class="stat-item">
      <span class="stat-label">Gross P&L</span>
      <span class="stat-value">{{ formatCurrency(trade.gross_pnl) }}</span>
    </div>

    <!-- Playbook -->
    <div class="stat-item">
      <span class="stat-label">Playbook</span>
      <span class="stat-value is-interactive">Select Playbook</span>
    </div>

    <!-- MAE / MFE -->
    <div class="stat-item maet-mfet-item">
      <span class="stat-label">MAET / MFET</span>
      <div class="maet-mfet-bar">
        <span class="maet-value">{{ formatCurrency(trade.maet) }}</span>
        <div class="bar-container">
          <div class="bar maet-bar" :style="{ width: `${maetWidth}%` }"></div>
          <div class="bar mfet-bar" :style="{ width: `${mfetWidth}%` }"></div>
        </div>
        <span class="mfet-value">{{ formatCurrency(trade.mfet) }}</span>
      </div>
    </div>

    <!-- Profit Target -->
    <div class="stat-item">
      <span class="stat-label">Profit Target</span>
      <span class="stat-value">{{ formatCurrency(trade.profit_target) }}</span>
    </div>

    <!-- Stop Loss -->
    <div class="stat-item">
      <span class="stat-label">Stop Loss</span>
      <span class="stat-value">{{ formatCurrency(trade.stop_loss) }}</span>
    </div>

    <!-- Initial Target -->
    <div class="stat-item">
      <span class="stat-label">Initial Target</span>
      <span class="stat-value is-positive">{{ formatCurrency(trade.initial_target) }}</span>
    </div>

    <!-- Trade Risk -->
    <div class="stat-item">
      <span class="stat-label">Trade Risk</span>
      <span class="stat-value" :class="tradeRisk.class">{{ tradeRisk.value }}</span>
    </div>

    <!-- Planned R-Multiple -->
    <div class="stat-item">
      <span class="stat-label">Planned R-Multiple</span>
      <span class="stat-value">{{ trade.planned_r_multiple }}R</span>
    </div>

    <!-- Realized R-Multiple -->
    <div class="stat-item">
      <span class="stat-label">Realized R-Multiple</span>
      <span class="stat-value" :class="realizedR.class">{{ realizedR.value }}</span>
    </div>

    <!-- Average Entry -->
    <div class="stat-item">
      <span class="stat-label">Average Entry</span>
      <span class="stat-value">{{ formatCurrency(trade.average_entry) }}</span>
    </div>

    <!-- Average Exit -->
    <div class="stat-item">
      <span class="stat-label">Average Exit</span>
      <span class="stat-value">{{ formatCurrency(trade.average_exit) }}</span>
    </div>

    <!-- Entry Time -->
    <div class="stat-item">
      <span class="stat-label">Entry Time</span>
      <span class="stat-value">{{ new Date(trade.entry_time).toLocaleTimeString() }}</span>
    </div>

    <!-- Exit Time -->
    <div class="stat-item">
      <span class="stat-label">Exit Time</span>
      <span class="stat-value">{{ new Date(trade.exit_time).toLocaleTimeString() }}</span>
    </div>

    <!-- Confluences -->
    <div class="stat-item">
      <span class="stat-label">Confluences</span>
      <span class="stat-value is-interactive">Select tag</span>
    </div>

    <!-- Entry Timeframe -->
    <div class="stat-item">
      <span class="stat-label">Entry Timeframe</span>
      <span class="stat-value is-interactive">Select Timeframe</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--semantic-size-stack-md) var(--semantic-size-stack-lg);
  padding-top: var(--semantic-size-inset-lg);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &.large-value {
    grid-column: 1 / -1; // Span full width
    flex-direction: column;
    align-items: flex-start;
    gap: var(--semantic-size-stack-xxs);

    .stat-value {
      font: var(--semantic-font-style-metric-display);
    }
  }
}

.stat-label {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
  font-weight: var(--base-font-weight-medium);

  &.is-positive {
    color: var(--semantic-color-feedback-positive-text);
  }

  &.is-negative {
    color: var(--semantic-color-feedback-negative-text);
  }

  &.is-interactive {
    color: var(--semantic-color-text-interactive);
    cursor: pointer; // Placeholder for interactivity
  }
}

.maet-mfet-item {
  grid-column: 1 / -1; // Span full width
}

.maet-mfet-bar {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  width: 60%; // Adjust as needed

  .maet-value {
    color: var(--semantic-color-feedback-positive-text);
    font: var(--semantic-font-style-data-numeric);
  }
  .mfet-value {
    color: var(--semantic-color-feedback-negative-text);
    font: var(--semantic-font-style-data-numeric);
  }
}

.bar-container {
  flex-grow: 1;
  display: flex;
  height: 8px;
  border-radius: var(--semantic-border-radius-tag);
  overflow: hidden;
}

.bar {
  height: 100%;
}

.maet-bar {
  background-color: var(--semantic-color-feedback-positive-text);
}

.mfet-bar {
  background-color: var(--semantic-color-feedback-negative-text);
}
</style>