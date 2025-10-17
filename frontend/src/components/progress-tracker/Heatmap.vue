<template>
  <div class="heatmap">
    <h3>Monthly Progress</h3>
    <div class="heatmap-grid">
      <div
        v-for="day in days"
        :key="day.date"
        class="heatmap-day"
        :style="{ backgroundColor: getDayColor(day.score) }"
        :title="`${day.date}: ${day.score}%`"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useDisciplineStore } from '../../stores/disciplineStore';

const disciplineStore = useDisciplineStore();

const summary = computed(() => disciplineStore.summary);

const days = computed(() => {
  if (!summary.value || !summary.value.score_history) {
    return [];
  }
  const days = [];
  const today = new Date();
  for (let i = 0; i < 35; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dateString = date.toISOString().slice(0, 10);
    days.push({
      date: dateString,
      score: summary.value.score_history[dateString] || 0,
    });
  }
  return days.reverse();
});

const getDayColor = (score) => {
  if (score === 0) {
    return '#ebedf0';
  }
  if (score < 25) {
    return '#c6e48b';
  }
  if (score < 50) {
    return '#7bc96f';
  }
  if (score < 75) {
    return '#239a3b';
  }
  return '#196127';
};

onMounted(() => {
  disciplineStore.fetchSummary();
});
</script>

<style scoped>
.heatmap {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.heatmap-day {
  width: 100%;
  padding-bottom: 100%;
  border-radius: 2px;
}
</style>