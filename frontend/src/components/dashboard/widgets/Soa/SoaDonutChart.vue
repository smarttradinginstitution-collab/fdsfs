<template>
  <div class="relative w-full h-48 md:h-full flex items-center justify-center">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
/**
 * @file SoaDonutChart.vue
 * @description
 * Renders a Doughnut chart to visualize the distribution of trades across
 * different SOA clusters, with an enhanced tooltip for detailed insights.
 */
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  /**
   * The cluster summary object from the SOA analysis.
   * Keys are cluster labels (e.g., 'A'), and values are objects
   * containing cluster metrics, including 'trade_count' and 'p_l'.
   * @type {Object}
   */
  clustersSummary: {
    type: Object,
    required: true,
  },
});

const CLUSTER_NAMES = {
  'A': 'Vincite Ottimali',
  'B': 'Stop Out / Breakeven',
  'C': 'Perdite Controllate',
  'D': 'Perdite da Reversal',
  'E': 'Vincite Sub-ottimali',
};

const chartData = computed(() => {
  const labels = Object.keys(props.clustersSummary);
  const data = labels.map(label => props.clustersSummary[label].trade_count);
  const totalTrades = data.reduce((acc, count) => acc + count, 0);

  // Calcola le percentuali per i tooltip
  const percentages = data.map(count => ((count / totalTrades) * 100).toFixed(1));

  return {
    labels: labels.map(label => `${label}: ${CLUSTER_NAMES[label] || 'Unknown'}`),
    datasets: [
      {
        backgroundColor: [
          '#4A90E2', // Blue (A)
          '#F5A623', // Orange (B)
          '#7ED321', // Green (C) -> Changed to green for controlled loss
          '#D0021B', // Red (D)
          '#9013FE', // Purple (E)
        ],
        data: data,
        // Passiamo dati extra qui per usarli nei tooltip
        percentages: percentages,
        pnl: labels.map(label => props.clustersSummary[label].p_l.toFixed(2)),
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#FFFFFF',
      },
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.dataset.labels[context.dataIndex] || '';
          const percentage = context.dataset.percentages[context.dataIndex];
          const pnl = context.dataset.pnl[context.dataIndex];
          return `${label}: ${percentage}% (Avg P/L: $${pnl})`;
        }
      }
    }
  },
};
</script>
