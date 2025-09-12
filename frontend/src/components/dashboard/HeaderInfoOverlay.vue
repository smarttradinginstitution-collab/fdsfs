<script setup>
import { ref } from 'vue';
import InfoIcon from '../icons/InfoIcon.vue';
import PopoverMenu from '../ui/PopoverMenu.vue';

const props = defineProps({
  infoText: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <div class="header-info-overlay">
    <slot name="title"></slot>
    <PopoverMenu>
      <template #trigger="{ toggle }">
        <InfoIcon class="info-icon" @click="toggle" />
      </template>
      <template #content>
        <div class="info-popover">
          <p>{{ infoText }}</p>
        </div>
      </template>
    </PopoverMenu>
  </div>
</template>

<style scoped>
.header-info-overlay {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.widget-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.info-icon {
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
}

.info-popover {
  padding: var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
}
</style>
