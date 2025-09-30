<template>
  <div class="metric-item">
    <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
      <template #title>
        <span class="metric-label">{{ label }}</span>
      </template>
      <template #content>
        <h4 class="info-overlay-title">{{ info.title }}</h4>
        <p class="info-overlay-text">{{ info.description }}</p>
      </template>
    </HeaderInfoOverlay>
    <p class="metric-value">{{ value }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import HeaderInfoOverlay from '@/components/ui/HeaderInfoOverlay.vue';
import { useMetricInfo } from '@/composables/useMetricInfo.js';

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  metricKey: { type: String, required: true },
});

const { info } = useMetricInfo(props.metricKey);
</script>

<style scoped>
.metric-item {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.metric-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.metric-value {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  font-weight: 600;
}

.metric-item :deep(.title-container) {
  align-items: center;
  justify-content: flex-start;
  gap: var(--semantic-size-stack-xxs);
}

.info-overlay-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.info-overlay-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}
</style>