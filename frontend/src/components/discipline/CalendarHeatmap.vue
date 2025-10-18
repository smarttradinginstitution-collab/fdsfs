<template>
  <div class="calendar-heatmap">
    <h3>Progress Tracker</h3>
    <div class="calendar-grid">
      <div v-for="day in days" :key="day.date" class="calendar-day" :style="{ backgroundColor: day.color }">
        <!-- Tooltip could be added here -->
      </div>
    </div>
    <div class="legend">
      <span>Less</span>
      <div class="legend-colors">
        <div class="legend-color-box" style="background-color: #ebedf0;"></div>
        <div class="legend-color-box" style="background-color: #9be9a8;"></div>
        <div class="legend-color-box" style="background-color: #40c463;"></div>
        <div class="legend-color-box" style="background-color: #30a14e;"></div>
        <div class="legend-color-box" style="background-color: #216e39;"></div>
      </div>
      <span>More</span>
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

const colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'];

for (let i = 1; i <= daysInMonth; i++) {
  days.value.push({
    date: i,
    color: colors[Math.floor(Math.random() * colors.length)] // Random color for now
  });
}
</script>

<style scoped>
.calendar-heatmap {
  width: 300px;
  padding: 1rem;
}

h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  width: 30px;
  height: 30px;
  background-color: #ebedf0;
  border-radius: 4px;
}

.legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  font-size: 0.8rem;
  color: var(--semantic-color-text-secondary);
}

.legend-colors {
  display: flex;
  gap: 4px;
}

.legend-color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}
</style>