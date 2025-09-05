<script setup>
import ArrowLeftIcon from '../icons/ArrowLeftIcon.vue';
import ArrowRightIcon from '../icons/ArrowRightIcon.vue';
import SettingsIcon from '../icons/SettingsIcon.vue';
import CameraIcon from '../icons/CameraIcon.vue';
import IconButton from '../ui/IconButton.vue';
import DropdownButton from '../ui/DropdownButton.vue';
import CalendarSettings from './CalendarSettings.vue';
import { useFilterStore } from '../../stores/filterStore';

const filterStore = useFilterStore();

defineProps({
  monthLabel: { type: String, default: 'Month Year' },
  monthlyPnl: { type: Number, default: 0 }
});

function formatPnl(pnl) {
  if (pnl === 0) return '$0.00';
  const sign = pnl > 0 ? '+' : '-';
  const value = Math.abs(pnl).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  return `${sign}${value}`;
}
</script>

<template>
  <div class="calendar-controls">
    <div class="controls-left">
      <div class="month-selector">
        <IconButton variant="tertiary" aria-label="Previous month" @click="filterStore.changeMonth(-1)">
          <ArrowLeftIcon />
        </IconButton>
        <span class="month-label">{{ monthLabel }}</span>
        <IconButton variant="tertiary" aria-label="Next month" @click="filterStore.changeMonth(1)">
          <ArrowRightIcon />
        </IconButton>
      </div>
    </div>
    <div class="controls-right">
      <div class="monthly-stats">
        <span class="stats-label">Monthly stats:</span>
        <span class="stats-value" :class="{ 'positive': monthlyPnl > 0, 'negative': monthlyPnl < 0 }">
          {{ formatPnl(monthlyPnl) }}
        </span>
      </div>
      <DropdownButton data-testid="calendar-settings-dropdown" :icon-only="true">
        <template #icon><SettingsIcon /></template>
        <template #content><CalendarSettings /></template>
      </DropdownButton>
      <IconButton variant="tertiary" aria-label="Take screenshot">
        <CameraIcon />
      </IconButton>
    </div>
  </div>
</template>

<style scoped>
.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-sm); /* Ridotto il margine inferiore */
  border-bottom: 1px solid var(--semantic-color-border-default);
  flex-shrink: 0;
}
.controls-left, .controls-right, .month-selector {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}
.month-label {
  font-family: var(--semantic-font-style-heading-xl-font-family);
  font-weight: var(--semantic-font-style-heading-xl-font-weight);
  font-size: clamp(
    var(--base-font-fluid-size-xl-min),
    1.2vw, /* Tweak ideal value for this context */
    var(--base-font-fluid-size-xl-max)
  );
  color: var(--semantic-color-text-primary);
  white-space: nowrap;
}
.monthly-stats {
  font-family: var(--semantic-font-style-body-sm-font-family);
  font-weight: var(--semantic-font-style-body-sm-font-weight);
  font-size: clamp(
    var(--base-font-fluid-size-lg-min), /* Usiamo una scala più grande */
    1vw, /* Valore ideale aggiustato */
    var(--base-font-fluid-size-lg-max)
  );
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}
/* Override IconButton size for this specific context */
.controls-left :deep(.icon-button),
.controls-right :deep(.icon-button) {
    width: clamp(1.75rem, 5vw, var(--base-size-component-button-min-height-sm));
    height: clamp(1.75rem, 5vw, var(--base-size-component-button-min-height-sm));
}
.stats-value {
  color: var(--semantic-color-text-primary);
  font-weight: var(--base-font-weight-medium);
  margin-left: var(--base-size-spacing-1);
}
.stats-value.positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stats-value.negative {
  color: var(--semantic-color-feedback-negative-text);
}
</style>
