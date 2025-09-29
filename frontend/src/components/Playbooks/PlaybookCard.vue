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
        <div class="stat-item win-rate-stat">
          <div class="donut-chart-container">
            <DoughnutChart :percentage="playbook.stats.win_rate" />
          </div>
          <div class="stat-value-label">
            <span class="value">{{ playbook.stats.win_rate.toFixed(1) }}%</span>
            <span class="label">Win Rate</span>
          </div>
        </div>

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

<script setup>
import { defineProps } from 'vue';
import BaseWidget from '../layout/BaseWidget.vue';
import DoughnutChart from './DoughnutChart.vue';

const props = defineProps({
  playbook: {
    type: Object,
    required: true,
  },
});

function formatCurrency(value) {
  if (typeof value !== 'number') {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}
</script>

<style scoped>
.playbook-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.playbook-card-link:hover {
  transform: translateY(-4px);
  box-shadow: var(--semantic-shadow-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.trade-count {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: var(--semantic-border-radius-pill);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem 1rem;
  padding-top: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.win-rate-stat {
  grid-column: span 1;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.donut-chart-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--semantic-color-surface-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value-label {
    display: flex;
    flex-direction: column;
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