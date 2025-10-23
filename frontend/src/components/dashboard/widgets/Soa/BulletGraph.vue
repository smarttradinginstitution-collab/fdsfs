<template>
  <div class="bullet-graph-container">
    <apexchart
      type="bar"
      height="100"
      :options="chartOptions"
      :series="series"
    ></apexchart>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: Number,
    required: true,
  },
  target: {
    type: Number,
    required: true,
  },
  ranges: {
    type: Array,
    required: true,
    validator: (value) =>
      value.length === 3 && value.every((v) => typeof v.value === 'number' && typeof v.color === 'string'),
  },
  labels: {
    type: Object,
    required: true,
  },
});

const series = computed(() => [
  {
    name: props.labels.value,
    data: [{ x: props.title, y: props.value }],
  },
]);

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    animations: { enabled: false }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '35%',
      distributed: false,
      dataLabels: {
        position: 'top',
      },
    },
  },
  colors: ['#FFFFFF'],
  dataLabels: {
    enabled: true,
    formatter: (val) => `${val.toFixed(2)}R`,
    style: {
      colors: ['#fff'],
      fontSize: '12px',
    },
    offsetX: 30,
  },
  xaxis: {
    categories: [props.title],
    labels: { show: false },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: { show: false },
  },
  grid: {
    show: false,
    padding: { top: -15, bottom: -10, left: 10, right: 10 }
  },
  legend: { show: false },
  tooltip: { enabled: false },
  annotations: {
    points: [
      {
        x: props.target,
        y: 0,
        marker: {
          size: 8,
          fillColor: '#fff',
          strokeColor: '#FF4560',
          radius: 2,
        },
        label: {
          text: `${props.labels.target}: ${props.target.toFixed(2)}R`,
          borderColor: '#FF4560',
          style: {
            color: '#fff',
            background: '#FF4560',
            fontSize: '11px',
            padding: { left: 5, right: 5, top: 2, bottom: 2 }
          },
        },
      },
    ],
    xaxis: props.ranges.map(range => ({
        x: 0,
        x2: range.value,
        fillColor: range.color,
        opacity: 0.3,
        label: {
            text: range.label,
            style: {
                background: 'transparent',
                color: '#fff',
                fontSize: '10px'
            }
        }
    }))
  },
}));
</script>

<style scoped>
.bullet-graph-container {
  position: relative;
}
</style>
