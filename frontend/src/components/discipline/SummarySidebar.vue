<template>
  <div class="summary-sidebar">
    <div class="summary-card">
      <h3 class="card-title">Current Streak</h3>
      <p class="streak-value">1 day <span class="emoji">😊</span></p>
    </div>
    <div class="summary-card">
      <h3 class="card-title">Current Period Score</h3>
      <div class="score-gauge" :style="{'--score-percent': `${score}%`}">
        <p class="score-percentage">{{ score }}%</p>
      </div>
    </div>
    <div class="summary-card">
      <h3 class="card-title">Today's progress</h3>
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
  gap: var(--semantic-size-stack-md);
  width: 250px; /* This could be a token if a standard sidebar width exists */
  flex-shrink: 0;
}

.summary-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
}

.card-title {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-sm);
}

.streak-value {
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
}

.emoji {
  font-size: var(--base-font-size-xl);
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
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
}

.progress-bar-container {
  width: 100%;
  height: 10px;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--base-border-radius-full);
  overflow: hidden;
  margin-bottom: var(--semantic-size-stack-xs);
}

.progress-bar {
  height: 100%;
  background-color: var(--semantic-color-interactive-primary-default);
  border-radius: var(--base-border-radius-full);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: right;
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
}
</style>