<template>
  <div :class="['skeleton-card', layoutClass]">
    <div class="skeleton-header">
      <div class="skeleton-icon"></div>
      <div class="skeleton-title"></div>
    </div>
    <div class="skeleton-description"></div>
    <div class="skeleton-stats">
      <div class="skeleton-stat-item"></div>
      <div class="skeleton-stat-item"></div>
      <div class="skeleton-stat-item"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue';

const props = defineProps({
  layout: {
    type: String,
    default: 'grid',
  },
});

const layoutClass = computed(() => {
  return props.layout === 'grid' ? 'layout-grid' : 'layout-list';
});
</script>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton-card {
  background-color: var(--color-background-muted);
  border-radius: var(--border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  animation: shimmer 2s infinite linear;
  background: linear-gradient(to right, var(--color-background-muted) 8%, var(--color-background-hover) 18%, var(--color-background-muted) 33%);
  background-size: 1000px 104px;
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
}

.skeleton-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  background-color: var(--color-background-subtle);
}

.skeleton-title {
  height: 24px;
  width: 60%;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background-subtle);
}

.skeleton-description {
  height: 40px;
  width: 100%;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background-subtle);
}

.skeleton-stats {
  display: flex;
  justify-content: space-between;
  gap: var(--semantic-size-stack-md);
  margin-top: auto; /* Push stats to the bottom */
}

.skeleton-stat-item {
  height: 20px;
  width: 30%;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background-subtle);
}

/* Specific styles for list layout */
.layout-list {
  flex-direction: row;
  align-items: center;
}

.layout-list .skeleton-header {
  flex-grow: 1;
}

.layout-list .skeleton-description {
 display: none; /* Hide description in list view for simplicity */
}

.layout-list .skeleton-stats {
  width: 40%;
  justify-content: flex-end;
}
</style>
