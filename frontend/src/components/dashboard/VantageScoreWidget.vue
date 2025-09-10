<template>
  <div class="vantage-score-widget">
    <!-- Header -->
    <div class="widget-header">
      <h2>Vantage Score</h2>
      <i>ⓘ</i>
    </div>

    <!-- Content (Chart) -->
    <div class="widget-content">
      <div v-if="statsStore.isLoading" class="loading-spinner">Loading...</div>
      <div v-else-if="statsStore.error" class="error-message">{{ statsStore.error }}</div>
      <div v-else-if="chartData" class="chart-container">
        <Radar :data="chartData" :options="chartOptions" />
      </div>
    </div>

    <!-- Footer -->
    <div class="widget-footer">
      <div class="score-display">
        <span>Your Vantage Score</span>
        <span class="score-value">{{ scoreValue.toFixed(2) }}</span>
      </div>
      <div class="linear-gauge">
        <div class="gauge-bar">
          <div class="gauge-indicator" :style="{ left: scorePosition }"></div>
        </div>
        <div class="gauge-labels">
          <span>0</span>
          <span>20</span>
          <span>40</span>
          <span>60</span>
          <span>80</span>
          <span>100</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'vue-chartjs';
import { useStatsStore } from '@/stores/statsStore';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const statsStore = useStatsStore();

// Usiamo i getter dello store
const chartData = computed(() => statsStore.vantageChartData);
const scoreValue = computed(() => statsStore.vantageScoreValue);

const scorePosition = computed(() => `${scoreValue.value}%`);

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      angleLines: {
        color: 'var(--semantic-color-border-default)',
      },
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      suggestedMin: 0,
      suggestedMax: 100,
      pointLabels: {
        font: {
          size: 12,
        },
        color: 'var(--semantic-color-text-secondary)',
      },
      ticks: {
        display: false, // Nascondiamo i tick numerici sull'asse radiale
      },
    },
  },
  plugins: {
    legend: {
      display: false, // La legenda è ridondante
    },
    tooltip: {
      callbacks: {
        label: function (context) {
          return `${context.label}: ${context.raw.toFixed(2)}`;
        },
      },
    },
  },
});

onMounted(() => {
  if (!statsStore.vantageScore) {
    statsStore.fetchVantageScore();
  }
});
</script>

<style scoped>
.vantage-score-widget {
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  max-width: 33.33%;
  aspect-ratio: 1 / 1.2; /* Invertito per rispettare larghezza/altezza */
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
  padding-bottom: var(--semantic-size-inset-md);
}

.widget-header h2 {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  margin: 0;
}

.widget-header i {
  font-style: normal;
  cursor: help;
}

.widget-content {
  flex-grow: 1;
  position: relative;
}

.chart-container {
  height: 100%;
}

.widget-footer {
  border-top: var(--base-border-width-1) solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.score-display {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.score-display span:first-child {
  font: var(--semantic-font-style-body-sm);
}

.score-display .score-value {
  font: var(--semantic-font-style-heading-2xl);
}

.linear-gauge {
  width: 100%;
}

.gauge-bar {
  width: 100%;
  height: 8px;
  background: linear-gradient(90deg, #f87171, #facc15, #4ade80);
  border-radius: 4px;
  position: relative;
}

.gauge-indicator {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background-color: white;
  border: 4px solid var(--semantic-color-interactive-primary-default);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 10px;
  color: var(--semantic-color-text-secondary);
}
</style>
