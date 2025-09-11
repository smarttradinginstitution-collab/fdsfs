<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import { Radar } from 'vue-chartjs';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import IconButton from '../ui/IconButton.vue';
import InfoIcon from '../icons/InfoIcon.vue';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const tradesStore = useTradesStore();

const vantageScore = computed(() => tradesStore.vantageScoreData);

const chartData = computed(() => {
  const metrics = vantageScore.value.metrics || [];
  // Colore derivato da --base-color-blue-600 (#2563eb)
  const blue600_rgb = '37, 99, 235';

  return {
    labels: metrics.map(m => m.label),
    datasets: [
      {
        label: 'Vantage Score',
        backgroundColor: `rgba(${blue600_rgb}, 0.2)`,
        borderColor: `rgba(${blue600_rgb}, 1)`,
        pointBackgroundColor: `rgba(${blue600_rgb}, 1)`,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: `rgba(${blue600_rgb}, 1)`,
        data: metrics.map(m => m.value),
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: {
        display: false,
        stepSize: 20,
      },
      grid: {
        color: 'var(--color-border-subtle)',
      },
      angleLines: {
        color: 'var(--color-border-subtle)',
      },
      pointLabels: {
        color: 'var(--color-text-secondary)',
        font: {
          // Chart.js font object is limited, so we approximate
          size: 12,
          family: 'Inter, sans-serif',
        },
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: true,
    },
  },
  elements: {
    line: {
      borderWidth: 2,
    },
  }
}));

const progressStyle = computed(() => ({
  width: `${vantageScore.value.score || 0}%`,
}));
</script>

<template>
  <div class="vantage-score-widget card">
    <div class="card-header">
      <h3 class="widget-title">Vantage Score</h3>
      <IconButton>
        <InfoIcon />
      </IconButton>
    </div>
    <div class="chart-container">
      <Radar v-if="vantageScore.metrics.length" :data="chartData" :options="chartOptions" />
      <div v-else class="loading-placeholder">Loading Chart...</div>
    </div>
    <div class="card-footer">
      <div class="footer-text">
        <span class="footer-title">Your Vantage Score</span>
        <span class="footer-value">{{ vantageScore.score ? vantageScore.score.toFixed(2) : '0.00' }}</span>
      </div>
      <div class="progress-container">
        <div class="progress-bar" :style="progressStyle"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: var(--color-background-card-primary);
  border: 1px solid var(--color-border-card-primary);
  border-radius: var(--semantic-border-radius-lg);
  box-shadow: var(--effect-shadow-small);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  color: var(--color-text-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  font: var(--typography-style-heading-h5);
}


.chart-container {
  position: relative;
  height: 250px;
}

.loading-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--color-text-secondary);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-stack-lg);
}

.footer-text {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.footer-title {
  font: var(--typography-style-body-medium);
  color: var(--color-text-secondary);
}

.footer-value {
  font: var(--typography-style-heading-h4);
}

.progress-container {
  flex-grow: 1;
  max-width: 100px;
  height: 8px;
  background-color: var(--color-background-interactive-secondary-disabled);
  border-radius: var(--semantic-border-radius-pill);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-background-warning-strong), var(--color-background-positive-strong));
  border-radius: var(--semantic-border-radius-pill);
  transition: width 0.5s ease-in-out;
}
</style>
