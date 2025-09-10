<script setup>
import { computed } from 'vue';
import { Radar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from 'chart.js';
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip
);

const props = defineProps({
  scores: {
    type: Object,
    required: true,
    default: () => ({
      profit_factor_score: 0,
      avg_win_loss_score: 0,
      max_drawdown_score: 0,
      win_rate_score: 0,
      consistency_score: 0,
      recovery_factor_score: 0,
    }),
  },
});

const { colors, isReady } = useChartColors();

const chartData = computed(() => {
  const labels = [
    'Profit Factor',
    'Avg Win/Loss',
    'Max Drawdown',
    'Win Rate',
    'Consistency',
    'Recovery Factor',
  ];
  const data = [
    props.scores.profit_factor_score,
    props.scores.avg_win_loss_score,
    props.scores.max_drawdown_score,
    props.scores.win_rate_score,
    props.scores.consistency_score,
    props.scores.recovery_factor_score,
  ];

  return {
    labels,
    datasets: [
      {
        label: 'Vantage Score Breakdown',
        data,
        backgroundColor: 'rgba(59, 130, 246, 0.2)', // Using blue from useChartColors neutral with manual alpha
        borderColor: colors.value.neutral,
        pointBackgroundColor: colors.value.neutral,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: colors.value.neutral,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    r: {
      angleLines: {
        color: 'var(--semantic-color-border-default)',
      },
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      pointLabels: {
        color: 'var(--semantic-color-text-secondary)',
        font: {
          size: 11,
        },
      },
      ticks: {
        color: 'var(--semantic-color-text-tertiary)',
        backdropColor: 'var(--semantic-color-surface-primary)',
        stepSize: 20,
      },
      suggestedMin: 0,
      suggestedMax: 100,
    },
  },
}));
</script>

<template>
  <div class="radar-chart-container">
    <Radar v-if="isReady" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.radar-chart-container {
  position: relative;
  height: 240px;
}
</style>
