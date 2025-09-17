<script setup>
import { useUiStore } from '../../../../stores/uiStore';
import BaseCheckbox from '../../../ui/BaseCheckbox.vue';
import { useMediaQuery } from '@vueuse/core';
import { watch } from 'vue';

const uiStore = useUiStore();
const isDesktop = useMediaQuery('(min-width: 769px)');

// Quando si passa alla visuale mobile, disattiviamo le opzioni non disponibili
watch(isDesktop, (isNowDesktop) => {
  if (!isNowDesktop) {
    if (uiStore.isWeeklySummaryVisible) {
      uiStore.toggleWeeklySummary();
    }
    if (uiStore.isCalendarWinRateVisible) {
      uiStore.toggleCalendarWinRate();
    }
  }
});

// Non c'è bisogno di una funzione handler separata,
// possiamo chiamare l'azione dello store direttamente dal template.
</script>

<template>
  <div class="settings-menu">
    <div class="category-group">
      <h4 class="category-header">Weekly</h4>
      <div class="settings-list">
        <template v-if="isDesktop">
          <div class="settings-item">
            <BaseCheckbox
              label="Show Weekly Summary"
              :model-value="uiStore.isWeeklySummaryVisible"
              @update:modelValue="uiStore.toggleWeeklySummary()"
            />
          </div>
        </template>
         <div v-else class="settings-item-disabled">
          Weekly summary is available on desktop only.
        </div>
      </div>
    </div>
    <div class="category-group">
      <h4 class="category-header">Daily</h4>
      <div class="settings-list">
        <div class="settings-item">
          <BaseCheckbox
            label="Show Trade Count"
            :model-value="uiStore.isCalendarTradeCountVisible"
            @update:modelValue="uiStore.toggleCalendarTradeCount()"
          />
        </div>
        <template v-if="isDesktop">
          <div class="settings-item">
            <BaseCheckbox
              label="Show Win Rate %"
              :model-value="uiStore.isCalendarWinRateVisible"
              @update:modelValue="uiStore.toggleCalendarWinRate()"
            />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-menu {
  padding: var(--semantic-size-inset-sm);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  min-width: 240px;
}
.category-group {
  padding-bottom: var(--semantic-size-stack-sm);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-subtle);
}
.category-group:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.category-header {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  padding: var(--semantic-size-inset-xs) 0;
}
.settings-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding-top: var(--semantic-size-stack-xs);
}
.settings-item-disabled {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
  padding: var(--semantic-size-inset-sm) 0;
}
</style>
