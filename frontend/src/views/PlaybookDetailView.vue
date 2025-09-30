<template>
  <div class="playbook-detail-view">
    <!-- Header -->
    <header class="view-header">
      <div class="breadcrumb">
        <router-link to="/playbooks">Playbook</router-link>
        <span class="breadcrumb-separator">/</span>
        <span v-if="!store.isAnalyticsLoading && store.currentPlaybookAnalytics" class="breadcrumb-current">{{ store.currentPlaybookAnalytics.title }}</span>
        <span v-else class="breadcrumb-current">Loading...</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-overview">{{ activeTab }}</span>
      </div>
      <div class="header-actions">
        <BaseButton v-if="activeTab === 'Playbook Rules'" @click="store.setCreatingGroup(true)">+ Create Group</BaseButton>
        <BaseButton v-else variant="secondary">Share</BaseButton>
      </div>
    </header>

    <!-- Tabs -->
    <nav class="tabs">
      <a
        v-for="tab in tabs"
        :key="tab"
        href="#"
        class="tab-item"
        :class="{ active: activeTab === tab }"
        @click.prevent="selectTab(tab)"
      >
        {{ tab }}
      </a>
    </nav>

    <!-- Main Content -->
    <main class="view-content">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'Overview'">
        <div v-if="store.isAnalyticsLoading" class="loading-state">
          <p>Loading analytics...</p>
        </div>
        <div v-else-if="store.error" class="error-state">
          <p>Error: {{ store.error }}</p>
        </div>
        <div v-else-if="store.currentPlaybookAnalytics" class="analytics-card">
          <div class="metrics-header">
              <button class="settings-button" aria-label="Settings">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style="width: 1.25rem; height: 1.25rem;">
                    <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.532 1.532 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.532 1.532 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106A1.532 1.532 0 0111.49 3.17zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                  </svg>
              </button>
          </div>
          <div class="metrics-grid">
              <MetricItem
                v-for="metric in formattedMetrics"
                :key="metric.key"
                :label="metric.label"
                :value="metric.value"
                :metricKey="metric.key"
              />
          </div>

          <div class="chart-section">
            <h3 class="chart-title">Daily Net Cumulative P&L</h3>
            <div class="chart-container">
              <Line v-if="store.currentPlaybookAnalytics?.equity_curve?.data?.length" :data="chartData" :options="chartOptions" />
              <div v-else class="chart-placeholder">No data to display.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Playbook Rules Tab -->
      <div v-if="activeTab === 'Playbook Rules'">
        <PlaybookRulesTab />
      </div>

      <!-- Other Tabs Placeholders -->
      <div v-if="activeTab === 'Executed Trades'">
        <p>Executed Trades will be displayed here.</p>
      </div>
      <div v-if="activeTab === 'Missed Trades'">
        <p>Missed Trades will be displayed here.</p>
      </div>
      <div v-if="activeTab === 'Notes'">
        <p>Notes will be displayed here.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import MetricItem from '@/components/analytics/MetricItem.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import PlaybookRulesTab from '@/components/Playbooks/PlaybookRulesTab.vue';
import { formatCurrency, formatNumber, formatPercentage } from '@/services/formatters.js';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const route = useRoute();
const store = usePlaybookStore();

const playbookId = computed(() => route.params.id);

// Tab management
const tabs = ['Overview', 'Playbook Rules', 'Executed Trades', 'Missed Trades', 'Notes'];
const activeTab = ref('Playbook Rules'); // Set "Playbook Rules" as the default active tab.

const selectTab = (tabName) => {
  activeTab.value = tabName;
  // Future logic for fetching data for other tabs can go here.
};

onMounted(() => {
  if (playbookId.value) {
    // Fetch analytics for the overview tab regardless
    store.fetchPlaybookAnalytics(playbookId.value);
  }
});

const formattedMetrics = computed(() => {
  const metrics = store.currentPlaybookAnalytics?.metrics;
  if (!metrics) return [];

  return [
    { key: 'netPnl', label: 'Net P&L', value: formatCurrency(metrics.net_pnl) },
    { key: 'trades', label: 'Trades', value: formatNumber(metrics.trades) },
    { key: 'winRate', label: 'Win Rate %', value: formatPercentage(metrics.win_rate) },
    { key: 'profitFactor', label: 'Profit Factor', value: metrics.profit_factor ? formatNumber(metrics.profit_factor, 2) : 'N/A' },
    { key: 'missedTrades', label: 'Missed Trades', value: formatNumber(metrics.missed_trades) },
    { key: 'expectancy', label: 'Expectancy', value: formatCurrency(metrics.expectancy) },
    { key: 'rulesFollowed', label: 'Rules Followed', value: formatPercentage(metrics.rules_followed) },
    { key: 'avgWinner', label: 'Average Winner', value: formatCurrency(metrics.average_winner) },
    { key: 'avgLoser', label: 'Average Loser', value: formatCurrency(metrics.average_loser) },
    { key: 'largestProfit', label: 'Largest Profit', value: formatCurrency(metrics.largest_profit) },
    { key: 'largestLoss', label: 'Largest Loss', value: formatCurrency(metrics.largest_loss) },
    { key: 'totalRMultiple', label: 'Total R Multiple', value: formatNumber(metrics.total_r_multiple, 2) },
  ];
});

const chartData = computed(() => {
  const equityCurve = store.currentPlaybookAnalytics?.equity_curve;
  if (!equityCurve) return { labels: [], datasets: [] };

  // Get color values from CSS tokens to make the chart theme-aware
  const primaryRgb = getComputedStyle(document.documentElement).getPropertyValue('--semantic-color-interactive-primary-rgb').trim();

  // Create a gradient for the background fill
  const ctx = document.createElement('canvas').getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 280); // Use the new chart height
  gradient.addColorStop(0, `rgba(${primaryRgb}, 0.4)`);
  gradient.addColorStop(1, `rgba(${primaryRgb}, 0)`);

  return {
    labels: equityCurve.labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        backgroundColor: gradient,
        borderColor: `rgb(${primaryRgb})`,
        data: equityCurve.data,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: `rgb(${primaryRgb})`,
        pointBorderColor: '#fff',
        pointHoverRadius: 7,
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: `rgb(${primaryRgb})`,
      },
    ],
  };
});

const chartOptions = computed(() => {
    // Get color values from CSS tokens to make the chart theme-aware
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--semantic-color-text-secondary').trim();
    const mutedBorderColor = getComputedStyle(document.documentElement).getPropertyValue('--semantic-color-border-muted').trim();

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: (context) => ` ${context.dataset.label}: ${formatCurrency(context.parsed.y)}`
                }
            },
        },
        scales: {
            x: {
                grid: {
                    display: true,
                    color: mutedBorderColor,
                },
                ticks: { color: textColor },
            },
            y: {
                grid: {
                    display: true,
                    color: mutedBorderColor,
                },
                ticks: {
                    color: textColor,
                    callback: (value) => formatCurrency(value)
                },
            },
        },
    };
});
</script>

<style scoped>
.playbook-detail-view {
  padding: 2rem;
  color: var(--semantic-color-text-primary);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font: var(--semantic-font-style-body-lg);
}

.breadcrumb-separator {
  color: var(--semantic-color-text-placeholder);
}

.breadcrumb-current {
    color: var(--semantic-color-text-primary);
    font-weight: 500;
}

.breadcrumb-overview {
    color: var(--semantic-color-text-secondary);
}

.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.tab-item {
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: var(--semantic-color-text-secondary);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px; /* Aligns with the container border */
}

.tab-item.active {
  color: var(--semantic-color-text-primary);
  border-bottom-color: var(--semantic-color-primary-default);
  font-weight: 500;
}

.view-content {
  /* The background is now on the card, not the whole content area */
}

.analytics-card {
    background-color: var(--semantic-color-surface-primary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    box-shadow: var(--semantic-effect-shadow-elevation-low);
    padding: var(--semantic-size-inset-md);
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-md);
}

.metrics-header {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    /* Reduce header impact */
    margin-bottom: -0.5rem;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: var(--semantic-size-stack-lg) var(--semantic-size-stack-md);
}

.settings-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--semantic-color-text-secondary);
}

.loading-state, .error-state {
    text-align: center;
    padding: 4rem;
    font: var(--semantic-font-style-body-lg);
    color: var(--semantic-color-text-secondary);
}

.chart-section {
  margin-top: var(--semantic-size-stack-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.chart-title {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-primary);
  font-weight: 500;
}

.chart-container {
  height: 280px;
  position: relative;
}

.chart-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  border-radius: var(--semantic-border-radius-container);
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-lg);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .playbook-detail-view {
    padding: 1rem;
  }
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>