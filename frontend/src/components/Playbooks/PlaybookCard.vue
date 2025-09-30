<script setup>
import { defineProps } from 'vue';
import BaseWidget from '../layout/BaseWidget.vue';
import DoughnutChart from './DoughnutChart.vue';
import { formatCurrency } from '@/services/formatters.js';

const props = defineProps({
  playbook: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <router-link :to="{ name: 'playbook-detail', params: { id: playbook.id } }" class="playbook-card-link">
    <BaseWidget>
      <template #header>
        <div class="card-header">
          <h3 class="widget-title">{{ playbook.title }}</h3>
          <span class="trade-count">{{ playbook.stats.total_trades }} Trades</span>
        </div>
      </template>

      <div class="stats-grid">
        <!-- Win Rate with Doughnut Chart -->
        <div class="stat-item win-rate-stat">
          <div class="donut-chart-container">
            <DoughnutChart :percentage="playbook.stats.win_rate" />
          </div>
          <div class="stat-value-label">
            <span class="value">{{ playbook.stats.win_rate.toFixed(1) }}%</span>
            <span class="label">Win Rate</span>
          </div>
        </div>

        <!-- Other Stats -->
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats.net_pnl) }}</span>
          <span class="label">Net PnL</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ playbook.stats.profit_factor ? playbook.stats.profit_factor.toFixed(2) : '∞' }}</span>
          <span class="label">Profit Factor</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats.expectancy) }}</span>
          <span class="label">Expectancy</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats.avg_winner) }}</span>
          <span class="label">Avg. Winner</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats.avg_loser) }}</span>
          <span class="label">Avg. Loser</span>
        </div>
      </div>
    </BaseWidget>
  </router-link>
</template>

<style scoped>
/* The link wrapper makes the entire card clickable without default link styles */
.playbook-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

/* The card header uses flexbox to align title and trade count */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
  /* Truncate long titles to prevent wrapping */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: var(--semantic-size-stack-sm); /* Space between title and badge */
}

.trade-count {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-pill);
  white-space: nowrap; /* Prevent badge from wrapping */
}

/* The grid for all the stats inside the widget's content area */
.stats-grid {
  display: grid;
  /* Create 3 responsive columns */
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: var(--semantic-size-stack-lg) var(--semantic-size-stack-md);
  /* Use the widget's content padding, no extra top padding needed */
  padding: var(--semantic-size-inset-lg);
  padding-top: var(--semantic-size-stack-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.win-rate-stat {
  flex-direction: row;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  /* Make win rate span across if needed, though auto-fit should handle it */
  grid-column: span 1;
}

.donut-chart-container {
  width: 40px;
  height: 40px;
  flex-shrink: 0; /* Prevent chart from shrinking */
}

.stat-value-label {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.stat-item .value {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-primary);
}

.stat-item .label {
  font: var(--semantic-font-style-body-xs);
  color: var(--semantic-color-text-secondary);
}
</style>