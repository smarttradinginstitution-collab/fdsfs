<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

// Import dei componenti custom
import KpiCard from '@/components/ui/KpiCard.vue';
import LineChart from '@/components/charts/LineChart.vue';
import GaugeChart from '@/components/charts/GaugeChart.vue';
import BarChart from '@/components/charts/BarChart.vue';

// Stato del componente
const summaryData = ref(null);
const isLoading = ref(true);
const error = ref(null);

// Hardcoded per questa implementazione, come da accordi
const tradingAccountId = '323aacbc-b72c-4129-a403-bb45d81e09b1';
const startDate = '2025-09-01';
const endDate = '2025-09-30';

// Funzione per il fetch dei dati
const fetchSummaryData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get(`/trades/summary/${tradingAccountId}`, {
      params: { start_date: startDate, end_date: endDate },
    });
    summaryData.value = response.data;
  } catch (err) {
    console.error('Errore nel caricamento dei dati di riepilogo:', err);
    error.value = 'Failed to load summary data.';
  } finally {
    isLoading.value = false;
  }
};

// Carica i dati al montaggio del componente
onMounted(fetchSummaryData);

// ---- Dati e opzioni per i grafici ----

// 1. Grafico Net Cumulative P&L (Line Chart)
const pnlLineChartData = computed(() => {
  if (!summaryData.value?.cumulative_pnl_series) {
    return { labels: [], datasets: [] };
  }
  const series = summaryData.value.cumulative_pnl_series;
  return {
    labels: series.labels.map(d => new Date(d).toLocaleDateString()),
    datasets: [
      {
        label: 'Cumulative P&L',
        data: series.data,
        borderColor: 'var(--semantic-color-feedback-positive-text)',
        backgroundColor: 'rgba(var(--semantic-color-feedback-positive-text-rgb), 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      },
    ],
  };
});

const pnlLineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
  },
  scales: {
    x: { display: false },
    y: { display: false },
  },
};

// 2. Grafico Profit Factor (Gauge Chart)
const profitFactorGaugeData = computed(() => {
    if (!summaryData.value?.stats) return { datasets: [] };
    const profitFactor = summaryData.value.stats.profit_factor || 0;
    // Il valore va da 0 a 10 (o più, ma normalizziamo a 10 per il gauge)
    const value = Math.min(profitFactor, 10);
    return {
        datasets: [{
            data: [value, 10 - value],
            backgroundColor: [
              'var(--semantic-color-feedback-positive-text)',
              'rgba(var(--semantic-color-text-tertiary-rgb), 0.2)',
            ],
            borderWidth: 0,
            circumference: 180,
            rotation: 270,
        }]
    };
});

// 3. Grafico Win % (Gauge Chart)
const winPercentageGaugeData = computed(() => {
    if (!summaryData.value?.stats) return { datasets: [] };
    const winRate = summaryData.value.stats.win_rate || 0;
    return {
        datasets: [{
            data: [winRate, 100 - winRate],
            backgroundColor: [
              'var(--semantic-color-feedback-positive-text)',
              'rgba(var(--semantic-color-text-tertiary-rgb), 0.2)',
            ],
            borderWidth: 0,
            circumference: 180,
            rotation: 270,
        }]
    };
});

const gaugeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '80%',
    plugins: {
        tooltip: { enabled: false }
    }
};

// 4. Grafico Avg Win/Loss (Bar Chart)
const avgWinLossBarData = computed(() => {
    if (!summaryData.value?.stats) return { labels: [], datasets: [] };
    const { avg_win, avg_loss } = summaryData.value.stats;
    return {
        labels: ['Win', 'Loss'],
        datasets: [{
            data: [avg_win, Math.abs(avg_loss)],
            backgroundColor: [
                'var(--semantic-color-feedback-positive-text)',
                'var(--semantic-color-feedback-negative-text)',
            ],
            borderRadius: 4,
            barPercentage: 0.5,
        }]
    }
});

const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
    },
    scales: {
        x: { display: false },
        y: { display: false }
    }
};

</script>

<template>
  <div v-if="isLoading" class="loading-state">
    <!-- Puoi inserire uno spinner o un messaggio di caricamento -->
    <p>Loading KPI data...</p>
  </div>
  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
  </div>
  <div v-else-if="summaryData" class="kpi-dashboard">
    <!-- 1. Card: Net Cumulative P&L -->
    <KpiCard>
      <template #title>Net Cumulative P&L</template>
      <div class="metric-container">
        <span class="metric-value">
            {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(summaryData.stats.net_pnl) }}
        </span>
        <div class="chart-wrapper line-chart">
          <LineChart :chart-data="pnlLineChartData" :chart-options="pnlLineChartOptions" />
        </div>
      </div>
    </KpiCard>

    <!-- 2. Card: Profit Factor -->
    <KpiCard>
      <template #title>Profit Factor</template>
       <div class="metric-container">
        <span class="metric-value">{{ summaryData.stats.profit_factor.toFixed(2) }}</span>
        <div class="chart-wrapper gauge-chart">
          <GaugeChart :chart-data="profitFactorGaugeData" :chart-options="gaugeOptions" />
        </div>
      </div>
    </KpiCard>

    <!-- 3. Card: Win % -->
    <KpiCard>
      <template #title>Win %</template>
       <div class="metric-container">
        <span class="metric-value">{{ summaryData.stats.win_rate.toFixed(2) }}%</span>
        <div class="chart-wrapper gauge-chart">
          <GaugeChart :chart-data="winPercentageGaugeData" :chart-options="gaugeOptions" />
        </div>
      </div>
    </KpiCard>

    <!-- 4. Card: Avg win/loss trade -->
    <KpiCard>
      <template #title>Avg win/loss trade</template>
      <div class="metric-container">
        <div class="values-wrapper">
            <span class="metric-value">{{ (summaryData.stats.avg_win / Math.abs(summaryData.stats.avg_loss)).toFixed(2) }}</span>
            <div class="avg-details">
                <span class="avg-win">
                    {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(summaryData.stats.avg_win) }}
                </span>
                <span class="avg-loss">
                    {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(summaryData.stats.avg_loss) }}
                </span>
            </div>
        </div>
        <div class="chart-wrapper bar-chart">
            <BarChart :chart-data="avgWinLossBarData" :chart-options="barOptions" />
        </div>
      </div>
    </KpiCard>
  </div>
</template>

<style scoped>
.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--semantic-size-stack-fluid-stat-card-gap);
}

.metric-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
}

.values-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
    line-height: 1;
}

.metric-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1;
}

.chart-wrapper {
  width: 120px;
  height: 50px;
}

.gauge-chart {
    height: 60px;
    align-self: center;
}

.bar-chart {
    width: 80px;
    height: 50px;
}

.avg-details {
    display: flex;
    gap: 16px;
    font: var(--semantic-font-style-data-numeric);
}

.avg-win {
    color: var(--semantic-color-feedback-positive-text);
}

.avg-loss {
    color: var(--semantic-color-feedback-negative-text);
}

.loading-state, .error-state {
    padding: 40px;
    text-align: center;
    font: var(--semantic-font-style-body-lg);
    color: var(--semantic-color-text-secondary);
}
</style>