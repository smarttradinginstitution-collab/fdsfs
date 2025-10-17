<template>
  <div class="summary-sidebar">
    <h2>Progress Tracker</h2>
    <div class="summary-item">
      <span>Current Streak</span>
      <span>{{ summary?.streak || 0 }} days</span>
    </div>
    <div class="summary-item">
      <span>Current Period Score</span>
      <span>{{ summary?.score_history ? (Object.values(summary.score_history).reduce((a, b) => a + b, 0) / Object.values(summary.score_history).length).toFixed(2) : 0 }}%</span>
    </div>
    <div class="summary-item">
      <span>Today's progress</span>
      <div class="progress-bar">
        <div
          class="progress"
          :style="{ width: `${todayProgress}%` }"
        ></div>
      </div>
      <span>{{ todayProgress.toFixed(2) }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useDisciplineStore } from '../../stores/disciplineStore';

const disciplineStore = useDisciplineStore();

const summary = computed(() => disciplineStore.summary);

const todayProgress = computed(() => {
  if (!summary.value || !summary.value.score_history) {
    return 0;
  }
  const today = new Date().toISOString().slice(0, 10);
  return summary.value.score_history[today] || 0;
});

onMounted(() => {
  disciplineStore.fetchSummary();
});
</script>

<style scoped>
.summary-sidebar {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-bar {
  width: 100px;
  height: 10px;
  background-color: #e5e7eb;
  border-radius: 5px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #3b82f6;
  border-radius: 5px;
}
</style>