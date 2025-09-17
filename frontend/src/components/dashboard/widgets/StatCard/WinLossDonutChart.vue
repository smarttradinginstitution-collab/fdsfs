<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useChartColors } from '../../../../composables/useChartColors';

ChartJS.register(ArcElement, Tooltip, Legend);

// ✅ default a 0 per evitare undefined/NaN
const props = defineProps({
  wins: { type: Number, required: true, default: 0 },
  losses: { type: Number, required: true, default: 0 },
  breakevens: { type: Number, required: true, default: 0 },
});

const { colors, isReady } = useChartColors();

// ✅ coercizione numerica e total pre-calcolato
const sanitized = computed(() => ({
  wins: Number(props.wins ?? 0),
  losses: Number(props.losses ?? 0),
  breakevens: Number(props.breakevens ?? 0),
}));
const total = computed(() => sanitized.value.wins + sanitized.value.losses + sanitized.value.breakevens);

const chartData = computed(() => ({
  datasets: [
    {
      data: [
        sanitized.value.wins,
        sanitized.value.losses,
        sanitized.value.breakevens
      ],
      backgroundColor: [
        colors.value.positive,
        colors.value.negative,
        colors.value.neutral,
      ],
      borderWidth: 0,
    },
  ],
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1,
  cutout: '75%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
    },
  },
}));
</script>

<template>
  <div class="donut-chart-container">
    <!-- ✅ niente NaN: renderizza solo se pronto e c'è almeno 1 valore // evitato errore props in console-->
    <Doughnut v-if="isReady && total > 0" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.donut-chart-container {
  width: 80%;
  height: 80%;
}
</style>
