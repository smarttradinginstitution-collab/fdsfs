<template>
  <div class="stat-item">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value">{{ value !== null && value !== undefined ? value : '--' }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: '--',
  },
});
</script>

<style lang="scss" scoped>
.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--fluid-spacing-xxs);
}

.stat-label {
  font-size: var(--fluid-font-size-m);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font-size: var(--fluid-font-size-l);
  font-weight: 600;
  color: var(--semantic-color-text-primary);
}
</style>