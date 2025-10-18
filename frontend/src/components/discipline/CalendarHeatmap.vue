<template>
  <div class="calendar-heatmap-container">
    <h3 class="card-title">Progress Tracker</h3>
    <div class="day-labels">
      <span v-for="day in dayLabels" :key="day">{{ day }}</span>
    </div>
    <div class="calendar-grid">
      <div v-for="day in days" :key="day.date" class="calendar-day" :style="{ backgroundColor: day.color }">
        <!-- Tooltip could be added here -->
      </div>
    </div>
    <div class="legend">
      <span class="legend-text">Less</span>
      <div class="legend-colors">
        <div class="legend-color-box" style="background-color: var(--semantic-color-surface-secondary);"></div>
        <div class="legend-color-box" style="background-color: #9be9a8;"></div>
        <div class="legend-color-box" style="background-color: #40c463;"></div>
        <div class="legend-color-box" style="background-color: #30a14e;"></div>
        <div class="legend-color-box" style="background-color: #216e39;"></div>
      </div>
      <span class="legend-text">More</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  heatmapData: {
    type: Array,
    required: true,
    default: () => [],
  },
});

const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const days = ref([]);

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth();

const colors = [
  'var(--semantic-color-surface-secondary)', // 0%
  '#9be9a8', // 1-25%
  '#40c463', // 26-50%
  '#30a14e', // 51-75%
  '#216e39', // 76-100%
];

function getColorForScore(score) {
  if (score === 0) return colors[0];
  if (score <= 0.25) return colors[1];
  if (score <= 0.50) return colors[2];
  if (score <= 0.75) return colors[3];
  return colors[4];
}

function generateCalendar() {
  const newDays = [];
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0=Sun, 1=Mon,...
  const dayOffset = (firstDayOfMonth === 0) ? 6 : firstDayOfMonth - 1; // Adjust to Mon-first week

  // Add blank days for offset
  for (let i = 0; i < dayOffset; i++) {
    newDays.push({ date: `blank-${i}`, color: 'transparent' });
  }

  // Populate days of the month
  for (let i = 1; i <= daysInMonth; i++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
    const dataForDay = props.heatmapData.find(d => d.date === dateStr);
    const score = dataForDay ? dataForDay.score : 0;

    newDays.push({
      date: i,
      color: getColorForScore(score),
    });
  }
  days.value = newDays;
}

watch(() => props.heatmapData, generateCalendar, { immediate: true, deep: true });

</script>

<style scoped>
.calendar-heatmap-container {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  width: 350px; /* Adjust width as needed */
  display: flex;
  flex-direction: column;
}

.card-title {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-md);
}

.day-labels {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font: var(--semantic-font-style-label-xs);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-xs);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: var(--semantic-size-stack-xxs);
}

.calendar-day {
  aspect-ratio: 1 / 1;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--base-border-radius-sm);
}

.legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-xs);
  margin-top: var(--semantic-size-stack-sm);
}

.legend-text {
  font: var(--semantic-font-style-label-xs);
  color: var(--semantic-color-text-secondary);
}

.legend-colors {
  display: flex;
  gap: var(--semantic-size-stack-xxs);
}

.legend-color-box {
  width: 15px;
  height: 15px;
  border-radius: var(--base-border-radius-xs);
}
</style>