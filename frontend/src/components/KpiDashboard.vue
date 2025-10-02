<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import KpiCard from '@/components/ui/KpiCard.vue';
// Chart components will be used in the next step, but I'll import them now.
import LineChart from '@/components/charts/LineChart.vue';
import GaugeChart from '@/components/charts/GaugeChart.vue';
import BarChart from '@/components/charts/BarChart.vue';

// Component State
const summaryData = ref(null);
const isLoading = ref(true);
const error = ref(null);
const dashboardEl = ref(null);

// Reactive refs for resolved CSS color variables, with fallbacks.
const positiveColor = ref('rgb(34, 197, 94)');
const negativeColor = ref('rgb(239, 68, 68)');
const tertiaryColor = ref('rgb(107, 114, 128)');
const colorsResolved = ref(false); // Flag to prevent race condition

/**
 * Extracts the numeric 'r, g, b' values from a CSS 'rgb(r, g, b)' string.
 * @param {string} rgbString - The color string (e.g., "rgb(34, 197, 94)").
 * @returns {string} The numeric part (e.g., "34, 197, 94").
 */
const getRgbValues = (rgbString) => {
  return rgbString.match(/\(([^)]+)\)/)?.[1] || '0, 0, 0';
};

// Hardcoded values as per requirements
const tradingAccountId = '323aacbc-b72c-4129-a403-bb45d81e09b1';
const startDate = '2025-09-01';
const endDate = '2025-09-30';

// Data Fetching
const fetchSummaryData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get(`/trades/summary/${tradingAccountId}`, {
      params: { start_date: startDate, end_date: endDate },
    });
    summaryData.value = response.data;
  } catch (err) {
    console.error('Error loading summary data:', err);
    error.value = 'Failed to load summary data.';
  } finally {
    isLoading.value = false;
  }
};

// Fetch data when the component is mounted
onMounted(async () => {
  await fetchSummaryData();

  // After the component is mounted and data is fetched, resolve the CSS variables
  if (dashboardEl.value) {
    const styles = getComputedStyle(dashboardEl.value);
    positiveColor.value = styles.getPropertyValue('--semantic-color-feedback-positive-text').trim();
    negativeColor.value = styles.getPropertyValue('--semantic-color-feedback-negative-text').trim();
    tertiaryColor.value = styles.getPropertyValue('--semantic-color-text-tertiary').trim();
    colorsResolved.value = true; // Signal that colors are ready
  }
});

// ---- Chart Data & Options ----

// Helper for number formatting
const formatCurrency = (value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

// 1. P&L Line Chart
const pnlLineChartData = computed(() => {
  // Guard against running before data and colors are ready, preventing race conditions.
  if (!summaryData.value || !colorsResolved.value) {
    return { labels: [], datasets: [] };
  }

  const series = summaryData.value.cumulative_pnl_series;
  const netPnl = summaryData.value.stats.net_pnl;

  // Conditionally choose the color based on P&L
  const chartColor = netPnl >= 0 ? positiveColor.value : negativeColor.value;

  return {
    labels: series.labels,
    datasets: [{
      data: series.data,
      borderColor: chartColor,
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      backgroundColor: (context) => {
        const { ctx, chartArea } = context.chart;
        if (!chartArea) {
          return 'rgba(0,0,0,0)'; // Fallback
        }
        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
        const rgb = getRgbValues(chartColor);
        gradient.addColorStop(0, `rgba(${rgb}, 0.4)`); // Top color
        gradient.addColorStop(1, `rgba(${rgb}, 0)`);   // Bottom color (fully transparent)
        return gradient;
      },
    }],
  };
});

const pnlLineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
  scales: { x: { display: false }, y: { display: false } },
};

// 2. Gauge Charts (Profit Factor & Win %)
const createGaugeData = (value, max) => {
  const normalizedValue = Math.min(Math.max(value, 0), max);
  return {
    datasets: [{
      data: [normalizedValue, max - normalizedValue],
      backgroundColor: [
        positiveColor.value,
        `rgba(${getRgbValues(tertiaryColor.value)}, 0.2)`,
      ],
      borderWidth: 0,
      circumference: 180,
      rotation: 270,
    }]
  };
};

const profitFactorGaugeData = computed(() => createGaugeData(summaryData.value?.stats?.profit_factor || 0, 10));
const winPercentageGaugeData = computed(() => createGaugeData(summaryData.value?.stats?.win_rate || 0, 100));

const gaugeOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  plugins: { tooltip: { enabled: false } }
};


// 3. Avg Win/Loss Bar Chart
const avgWinLossBarData = computed(() => {
    if (!summaryData.value?.stats) return { labels: [], datasets: [] };
    const { avg_win, avg_loss } = summaryData.value.stats;
    return {
        labels: ['Win', 'Loss'],
        datasets: [{
            data: [avg_win, Math.abs(avg_loss)],
            backgroundColor: [
                positiveColor.value,
                negativeColor.value,
            ],
            borderWidth: 0,
            borderRadius: 4,
        }]
    }
});

const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
    },
    scales: {
        x: { display: false, grid: { display: false } },
        y: { display: false, grid: { display: false } }
    }
};

</script>

<template>
  <div v-if="isLoading" class="loading-state">
    <p>Loading KPI data...</p>
  </div>
  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
  </div>
  <div v-else-if="summaryData" ref="dashboardEl" class="kpi-dashboard">
    <!-- Card 1: Net Cumulative P&L (New 3-Row Layout) -->
    <KpiCard class="pnl-card-layout">
      <div class="pnl-header">
        <h3 class="card-title">Net Cumulative P&L</h3>
        <span class="trade-badge">{{ summaryData.stats.trade_count }} trades</span>
      </div>
      <div class="pnl-metric">
        <p class="metric-value">{{ formatCurrency(summaryData.stats.net_pnl) }}</p>
      </div>
      <div class="pnl-chart-area">
        <LineChart :chart-data="pnlLineChartData" :chart-options="pnlLineChartOptions" />
      </div>
    </KpiCard>

    <!-- Card 2: Profit Factor -->
    <KpiCard class="card-layout-horizontal">
      <div class="text-content">
        <h3 class="card-title">Profit Factor</h3>
        <p class="metric-value">{{ summaryData.stats.profit_factor.toFixed(2) }}</p>
      </div>
      <div class="chart-content gauge-chart-wrapper">
        <GaugeChart :chart-data="profitFactorGaugeData" :chart-options="gaugeOptions" />
      </div>
    </KpiCard>

    <!-- Card 3: Win % -->
    <KpiCard class="card-layout-horizontal">
      <div class="text-content">
        <h3 class="card-title">Win %</h3>
        <p class="metric-value">{{ summaryData.stats.win_rate.toFixed(2) }}%</p>
      </div>
      <div class="chart-content gauge-chart-wrapper">
        <GaugeChart :chart-data="winPercentageGaugeData" :chart-options="gaugeOptions" />
      </div>
    </KpiCard>

    <!-- Card 4: Avg win/loss trade -->
    <KpiCard class="card-layout-vertical">
        <div class="top-row">
            <h3 class="card-title">Avg win/loss trade</h3>
            <p class="metric-value">{{ (summaryData.stats.avg_win / Math.abs(summaryData.stats.avg_loss)).toFixed(2) }}</p>
        </div>
        <div class="bottom-row">
            <div class="bar-chart-wrapper">
                <BarChart :chart-data="avgWinLossBarData" :chart-options="barOptions" />
            </div>
            <div class="bar-labels">
                <span class="avg-win">{{ formatCurrency(summaryData.stats.avg_win) }}</span>
                <span class="avg-loss">{{ formatCurrency(summaryData.stats.avg_loss) }}</span>
            </div>
        </div>
    </KpiCard>
  </div>
</template>

<style scoped>
/* Main Dashboard Grid */
.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--semantic-size-stack-fluid-stat-card-gap);
}

/* Base Card Title Style */
.card-title {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

/* Main Metric Value Style */
.metric-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 0.4;
}

/* --- Card 1: PnL 3-Row Layout --- */
.pnl-card-layout {
  flex-direction: column;
  justify-content: flex-start;
  gap: var(--base-size-fluid-spacing-xs); /* Fluid Gap */
}

.pnl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.trade-badge {
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--base-size-fluid-spacing-badge-padding-y) var(--base-size-fluid-spacing-badge-padding-x); /* Fluid Padding */
  border-radius: var(--semantic-border-radius-tag, 999px);
  font: var(--semantic-font-style-label-sm); /* Corrected to fluid font token */
  color: var(--semantic-color-text-secondary);
}

.pnl-metric {
  padding-top: var(--base-size-fluid-spacing-xxs); /* Fluid Padding */
  padding-bottom: var(--base-size-fluid-spacing-sm); /* Fluid Padding */
}

.pnl-chart-area {
  margin-top: -38px;
  margin-bottom: -10px; /* Adjust to pull chart closer */
  flex-grow: 1;
  width: 100%;
  min-height: 40px;
  height: 70px;
}


/* --- Card 2 & 3: Horizontal Layout --- */
.card-layout-horizontal {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: var(--base-size-fluid-spacing-md); /* Fluid Gap */
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--base-size-fluid-spacing-xxs); /* Fluid Gap */
}

.chart-content {
  flex-shrink: 0;
}

.line-chart-wrapper {
  width: 140px;
  height: 60px;
}

.gauge-chart-wrapper {
  width: 80px;
  height: 60px;
}

/* --- Card 4: Vertical Layout --- */
.card-layout-vertical {
  flex-direction: column;
  justify-content: space-between;
  gap: var(--base-size-fluid-spacing-sm); /* Fluid Gap */
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.bottom-row {
  display: flex;
  flex-direction: column;
  gap: var(--base-size-fluid-spacing-xs); /* Fluid Gap */
}

.bar-chart-wrapper {
  width: 100%;
  height: 24px;
}

.bar-labels {
    display: flex;
    justify-content: space-between;
    font: var(--semantic-font-style-data-numeric);
}

.avg-win {
  color: var(--semantic-color-feedback-positive-text);
}

.avg-loss {
  color: var(--semantic-color-feedback-negative-text);
}


/* Loading and Error States */
.loading-state, .error-state {
  padding: 40px;
  text-align: center;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  grid-column: 1 / -1;
}
</style>