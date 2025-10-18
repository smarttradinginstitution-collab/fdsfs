<template>
  <div class="summary-sidebar">
    <div class="summary-card">
      <h3>Current Streak</h3>
      <p class="streak-value">1 day <span class="emoji">😊</span></p>
    </div>
    <div class="summary-card">
      <h3>Current Period Score</h3>
      <div class="score-gauge">
        <p class="score-percentage">{{ score }}%</p>
      </div>
    </div>
    <div class="summary-card">
      <h3>Today's progress</h3>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progressWidth }"></div>
      </div>
      <p class="progress-text">{{ completed }}/{{ total }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  score: {
    type: Number,
    required: true,
    default: 0
  },
  completed: {
    type: Number,
    required: true,
    default: 0
  },
  total: {
    type: Number,
    required: true,
    default: 0
  }
});

const progressWidth = computed(() => {
  if (props.total === 0) return '0%';
  return `${(props.completed / props.total) * 100}%`;
});
</script>

<style scoped>
.summary-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 250px;
  flex-shrink: 0;
}

.summary-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-container);
  padding: 1.5rem;
  box-shadow: var(--semantic-shadow-sm);
}

h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.streak-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--semantic-color-text-primary);
}

.emoji {
  font-size: 1.5rem;
}

.score-gauge {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    var(--semantic-color-interactive-primary-default) 0% var(--score-percent, 0%),
    var(--semantic-color-surface-secondary) var(--score-percent, 0%) 100%
  );
  display: grid;
  place-items: center;
  margin: 0 auto;
}

.score-percentage {
  font-size: 2rem;
  font-weight: 700;
  color: var(--semantic-color-text-primary);
}

.progress-bar-container {
  width: 100%;
  height: 10px;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background-color: var(--semantic-color-interactive-primary-default);
  border-radius: 5px;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: right;
  font-size: 0.9rem;
  color: var(--semantic-color-text-secondary);
}
</style>