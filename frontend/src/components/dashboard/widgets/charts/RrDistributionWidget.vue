<script setup>
import { computed, ref } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTradesStore } from '../../../../stores/trades';
import { useChartColors } from '../../../../composables/useChartColors';
import { useChartResize } from '../../../../composables/useChartResize';
import BaseWidget from '../../../layout/BaseWidget.vue';
import HeaderInfoOverlay from '../../../ui/HeaderInfoOverlay.vue';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const tradesStore = useTradesStore();
const { feedbackColors, gridColors, isReady } = useChartColors();
const chartRef = ref(null);

useChartResize(chartRef);

const rrDistributionData = computed(() => tradesStore.getRrDistributionData);

const chartData = computed(() => {
  if (!rrDistributionData.value || !isReady.value) {
    return { labels: [], datasets: [] };
  }

  const data = rrDistributionData.value.datasets[0].data;
  const labels = rrDistributionData.value.labels;

  const backgroundColors = [
    ...Array(3).fill(feedbackColors.value.negative),
    ...Array(3).fill(feedbackColors.value.positive),
  ];

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor: backgroundColors,
        borderRadius: 4,
        barPercentage: 0.8,
        categoryPercentage: 0.7,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0,
        color: gridColors.value?.ticks || '#909093',
      },
      grid: {
        drawOnChartArea: true,
        drawTicks: false,
        color: gridColors.value?.line || '#d8d8d9',
      },
    },
    x: {
      ticks: {
        color: gridColors.value?.ticks || '#909093',
      },
      grid: {
        display: false,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: true,
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += `${context.parsed.y} trades`;
          }
          return label;
        },
      },
    },
  },
}));
</script>

<template>
  <BaseWidget>
    <template #header>
      <HeaderInfoOverlay aria-label="View information about the RR Distribution chart">
        <template #title>
          <h3 class="widget-title">RR Distribution</h3>
        </template>
        <template #content>
          <h4 class="info-overlay-title">About this Chart</h4>
          <p class="info-overlay-text">
            The Risk/Reward (RR) Distribution chart shows the number of trades taken at different RR ratios. It helps you understand if you are respecting your strategy's risk management rules.
          </p>
        </template>
      </HeaderInfoOverlay>
    </template>

    <div class="chart-container">
      <Bar v-if="isReady" ref="chartRef" :data="chartData" :options="chartOptions" />
    </div>
  </BaseWidget>
</template>

<style scoped>
.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 250px;
}

.info-overlay-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.info-overlay-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}
</style>
