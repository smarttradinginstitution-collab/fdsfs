<script setup>
import { defineProps, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import DoughnutChart from './DoughnutChart.vue';
import { formatCurrency } from '@/services/formatters.js';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';

const playbookStore = usePlaybookStore();

const props = defineProps({
  playbook: {
    type: Object,
    required: true,
  },
  layout: {
    type: String,
    default: 'grid',
  },
});

const statsGridClass = computed(() => {
  return props.layout === 'grid' ? 'layout-grid' : '';
});

async function handleDelete(closeMenu) {
  closeMenu();
  if (window.confirm('Are you sure you want to delete this playbook?')) {
    try {
      await playbookStore.deletePlaybook(props.playbook.id);
      // Optionally, show a success notification here
    } catch (error) {
      // Optionally, show an error notification here
      console.error('Failed to delete playbook:', error);
    }
  }
}
</script>

<template>
  <BaseWidget>
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <h3 class="widget-title">{{ playbook.title }}</h3>
          <span class="trade-count">{{ playbook.stats?.total_trades || 0 }} Trades</span>
        </div>
        <ActionsMenu @click.stop>
          <template #content="{ closeMenu }">
            <router-link :to="{ name: 'playbook-edit', params: { id: playbook.id } }" class="menu-item" @click="closeMenu">
              Edit
            </router-link>
            <div class="menu-item menu-item-danger" @click="handleDelete(closeMenu)">
              Delete
            </div>
          </template>
        </ActionsMenu>
      </div>
    </template>

    <router-link :to="{ name: 'playbook-detail', params: { id: playbook.id } }" class="playbook-card-link">
      <div class="stats-grid" :class="statsGridClass">
        <!-- Win Rate with Doughnut Chart -->
        <div class="stat-item win-rate-stat">
          <div class="donut-chart-container">
            <DoughnutChart :percentage="playbook.stats?.win_rate || 0" />
          </div>
          <div class="stat-value-label">
            <span class="value">{{ (playbook.stats?.win_rate || 0).toFixed(1) }}%</span>
            <span class="label">Win Rate</span>
          </div>
        </div>

        <!-- Other Stats -->
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats?.net_pnl || 0) }}</span>
          <span class="label">Net PnL</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ playbook.stats?.profit_factor ? playbook.stats.profit_factor.toFixed(2) : 'N/A'
            }}</span>
          <span class="label">Profit Factor</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats?.expectancy || 0) }}</span>
          <span class="label">Expectancy</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats?.avg_winner || 0) }}</span>
          <span class="label">Avg. Winner</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatCurrency(playbook.stats?.avg_loser || 0) }}</span>
          <span class="label">Avg. Loser</span>
        </div>
      </div>
    </router-link>
  </BaseWidget>
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

.header-left {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  /* This will allow the title to take up available space and truncate */
  overflow: hidden;
  flex: 1;
}

.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
  /* Truncate long titles to prevent wrapping */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: var(--semantic-size-stack-sm);
  /* Space between title and badge */
}

.trade-count {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
  white-space: nowrap;
  /* Prevent badge from wrapping */
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

/* When in grid view, force a 3-column layout for the stats */
.stats-grid.layout-grid {
  grid-template-columns: repeat(3, 1fr);
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
  flex-shrink: 0;
  /* Prevent chart from shrinking */
}

.stat-value-label {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.stat-item .value {
  font: var(--semantic-font-style-body-sm);
  font-weight: 600;
  /* Medium weight to make it stand out */
  color: var(--semantic-color-text-primary);
}

.stat-item .label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}
</style>