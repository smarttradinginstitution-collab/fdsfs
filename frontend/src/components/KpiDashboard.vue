<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import KpiCard from '@/components/ui/KpiCard.vue';
// Chart components will be used in the next step, but I'll import them now.
import LineChart from '@/components/charts/LineChart.vue';
import GaugeChart from '@/components/charts/GaugeChart.vue';
import BarChart from '@/components/charts/BarChart.vue';
import PopoverMenu from '@/components/ui/PopoverMenu.vue';
import IconButton from '@/components/ui/IconButton.vue';
import InfoIcon from '@/components/icons/InfoIcon.vue';

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
 * Converts any valid CSS color string (rgb or hex) into its numeric 'r, g, b' components.
 * @param {string} colorString - The color string (e.g., "rgb(34, 197, 94)" or "#22c55e").
 * @returns {string} The numeric part (e.g., "34, 197, 94").
 */
const getRgbValues = (colorString) => {
  if (!colorString) return '0, 0, 0';

  // Handle rgb(r, g, b) format
  if (colorString.startsWith('rgb')) {
    return colorString.substring(colorString.indexOf('(') + 1, colorString.lastIndexOf(')'));
  }

  // Handle hex format (#RRGGBB or #RGB)
  if (colorString.startsWith('#')) {
    let hex = colorString.slice(1);
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    if (hex.length === 3) {
      hex = hex.split('').map(char => char + char).join('');
    }

    if (hex.length === 6) {
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);
      return `${r}, ${g}, ${b}`;
    }
  }

  // Fallback for other formats or errors
  console.warn(`Could not parse color: ${colorString}, falling back to black.`);
  return '0, 0, 0';
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

// 2. Meter Charts (Doughnut/Gauge) - Final Color Logic
const createMeterData = (value, max) => {
  const normalizedValue = Math.min(Math.max(value, 0), max);
  return {
    datasets: [{
      data: [normalizedValue, max - normalizedValue],
      backgroundColor: [
        positiveColor.value, // Value part is always green
        negativeColor.value, // Empty part is always red
      ],
      borderWidth: 0,
    }]
  };
};

const profitFactorChartData = computed(() => {
  if (!summaryData.value) return { datasets: [] };
  return createMeterData(summaryData.value.stats.profit_factor || 0, 10);
});

const winPercentageChartData = computed(() => {
  if (!summaryData.value) return { datasets: [] };
  return createMeterData(summaryData.value.stats.win_rate || 0, 100);
});

const gaugeOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  plugins: { tooltip: { enabled: false } },
  circumference: 180, // Presentation option for semi-circle
  rotation: 270,      // Presentation option for semi-circle
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  plugins: { tooltip: { enabled: false } },
  circumference: 360, // Presentation option for full circle
};


// 3. Avg Win/Loss Bar Chart - This is now handled with CSS Flexbox, so no chart config is needed.

</script>

<template>
  <div v-if="isLoading" class="loading-state">
    <p>Loading KPI data...</p>
  </div>
  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
  </div>
  <div v-else-if="summaryData" ref="dashboardEl" class="kpi-dashboard">
    <!-- Card 1: Net Cumulative P&L -->
    <KpiCard class="pnl-card-layout">
      <div class="pnl-header">
        <div class="card-title-wrapper">
          <h3 class="card-title">Net Cumulative P&L</h3>
          <PopoverMenu>
            <template #trigger="{ toggle }">
              <IconButton @click.stop="toggle" aria-label="Net Cumulative P&L Information" size="small" class="info-button">
                <InfoIcon />
              </IconButton>
            </template>
            <template #content>
              <div class="popover-content">
                The total net profit or loss (P&L) from all trades over a specific period. It's the account's bottom-line performance.
              </div>
            </template>
          </PopoverMenu>
        </div>
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
        <div class="card-title-wrapper">
          <h3 class="card-title">Profit Factor</h3>
          <PopoverMenu>
            <template #trigger="{ toggle }">
              <IconButton @click.stop="toggle" aria-label="Profit Factor Information" size="small" class="info-button">
                <InfoIcon />
              </IconButton>
            </template>
            <template #content>
              <div class="popover-content">
                Measures profitability by dividing the total gross profits by the total gross losses. A value over 1.0 indicates a profitable system.
              </div>
            </template>
          </PopoverMenu>
        </div>
        <p class="metric-value">{{ summaryData.stats.profit_factor.toFixed(2) }}</p>
      </div>
      <div class="chart-content gauge-chart-wrapper">
        <GaugeChart :chart-data="profitFactorChartData" :chart-options="doughnutOptions" />
      </div>
    </KpiCard>

    <!-- Card 3: Win % -->
    <KpiCard class="card-layout-horizontal">
      <div class="text-content">
        <div class="card-title-wrapper">
          <h3 class="card-title">Win %</h3>
          <PopoverMenu>
            <template #trigger="{ toggle }">
              <IconButton @click.stop="toggle" aria-label="Win % Information" size="small" class="info-button">
                <InfoIcon />
              </IconButton>
            </template>
            <template #content>
              <div class="popover-content">
                The percentage of total trades that were closed for a profit, indicating the frequency of success.
              </div>
            </template>
          </PopoverMenu>
        </div>
        <p class="metric-value">{{ summaryData.stats.win_rate.toFixed(2) }}%</p>
      </div>
      <div class="chart-content gauge-chart-wrapper">
        <GaugeChart :chart-data="winPercentageChartData" :chart-options="gaugeOptions" />
      </div>
    </KpiCard>

    <!-- Card 4: Avg win/loss trade -->
    <KpiCard class="avg-win-loss-layout">
      <div class="card-header">
        <div class="card-title-wrapper">
          <h3 class="card-title">Avg win/loss trade</h3>
          <PopoverMenu>
            <template #trigger="{ toggle }">
              <IconButton @click.stop="toggle" aria-label="Average win/loss trade Information" size="small" class="info-button">
                <InfoIcon />
              </IconButton>
            </template>
            <template #content>
              <div class="popover-content">
                The ratio of the average profit on winning trades to the average loss on losing trades. It measures the risk/reward relationship of the strategy.
              </div>
            </template>
          </PopoverMenu>
        </div>
        <p class="main-metric-value">{{ (summaryData.stats.avg_win / Math.abs(summaryData.stats.avg_loss)).toFixed(2) }}</p>
      </div>
      <div class="chart-block">
        <div class="segmented-bar">
          <div class="win-segment" :style="{ flexGrow: summaryData.stats.avg_win }"></div>
          <div class="loss-segment" :style="{ flexGrow: Math.abs(summaryData.stats.avg_loss) }"></div>
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

.card-title-wrapper {
  display: flex;
  align-items: baseline; /* Use baseline alignment for perfect text-to-icon centering */
  gap: var(--base-size-fluid-spacing-xs);
}

.info-button {
  color: var(--semantic-color-text-tertiary);
}
.info-button:hover {
  color: var(--semantic-color-text-primary);
}

.popover-content {
  padding: var(--semantic-size-inset-sm);
  max-width: 250px;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
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

/* --- Sostituzione per Card 4: Layout Avg Win/Loss --- */

/* Contenitore principale della card, impilato verticalmente */
.avg-win-loss-layout {
  flex-direction: column;
  justify-content: flex-start; /* Allinea il contenuto in alto */
  gap: var(--base-size-fluid-spacing-sm); /* Spazio tra header e blocco grafico */
}

/* Riga 1: Contiene titolo e valore principale */
.card-header {
  display: flex;
  justify-content: space-between; /* Spinge titolo e valore ai lati opposti */
  align-items: flex-start; /* Allinea in alto */
  width: 100%;
}

/* Stile per il valore principale (es. 2.75) */
.main-metric-value {
  /* Assicurati che i token per font e colore siano corretti */
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1; /* Aggiusta la linea per un allineamento pulito */
}

/* Riga 2: Contiene la barra e le sue etichette */
.chart-block {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: var(--base-size-fluid-spacing-xs); /* Spazio tra barra ed etichette */
}

/* Contenitore della barra segmentata */
.segmented-bar {
  display: flex; /* FONDAMENTALE per creare i segmenti */
  width: 100%;
  height: 8px; /* Altezza della barra ridotta */
  border-radius: var(--semantic-border-radius-tag, 999px); /* Angoli arrotondati */
  overflow: hidden; /* Nasconde gli angoli interni dei segmenti */
}

/* Stile del segmento VERDE */
.win-segment {
  background-color: var(--semantic-color-feedback-positive-text);
  height: 100%;
}

/* Stile del segmento ROSSO */
.loss-segment {
  background-color: var(--semantic-color-feedback-negative-text);
  height: 100%;
}

/* Contenitore per le etichette sotto la barra */
.bar-labels {
  display: flex;
  justify-content: space-between; /* Spinge le etichette ai lati */
  width: 100%;
  font: var(--semantic-font-style-body-sm); /* Usa un font di corpo standard */
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