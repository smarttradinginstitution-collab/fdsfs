<template>
  <div class="calendar-heatmap">
    <h3 class="card-title">Progress Tracker</h3>
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
import { ref } from 'vue';

// Placeholder data for the calendar heatmap
const days = ref([]);
const today = new Date();
const year = today.getFullYear();
const month = today.getMonth();
const daysInMonth = new Date(year, month + 1, 0).getDate();

const colors = ['var(--semantic-color-surface-secondary)', '#9be9a8', '#40c463', '#30a14e', '#216e39'];

for (let i = 1; i <= daysInMonth; i++) {
  days.value.push({
    date: i,
    color: colors[Math.floor(Math.random() * colors.length)] // Random color for now
  });
}
</script>

<style scoped>
.calendar-heatmap {
  width: 300px; /* This could be a token if a standard width exists */
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
}

.card-title {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-md);
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