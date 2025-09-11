<script setup>
import { ref, onMounted } from 'vue';
import HoverPopover from './HoverPopover.vue';
import PopoverMenu from './PopoverMenu.vue'; // The click-based popover
import IconButton from './IconButton.vue';
import InfoIcon from '../icons/InfoIcon.vue';

const isTouchDevice = ref(false);

onMounted(() => {
  // Simple and effective check for touch capabilities.
  isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
});
</script>

<template>
  <div>
    <!-- RENDER FOR TOUCH DEVICES (Click-based) -->
    <PopoverMenu v-if="isTouchDevice">
      <template #trigger="{ toggle }">
        <IconButton @click="toggle" class="info-button">
          <InfoIcon />
        </IconButton>
      </template>
      <template #content>
        <div class="info-popover-content">
          <slot></slot>
        </div>
      </template>
    </PopoverMenu>

    <!-- RENDER FOR NON-TOUCH DEVICES (Hover-based) -->
    <HoverPopover v-else>
      <template #trigger>
        <IconButton class="info-button">
          <InfoIcon />
        </IconButton>
      </template>
      <template #content>
        <div class="info-popover-content">
          <slot></slot>
        </div>
      </template>
    </HoverPopover>
  </div>
</template>

<style scoped>
/* These styles apply to both versions, keeping the look consistent. */
.info-button {
  color: var(--semantic-color-text-tertiary);
}
.info-button:hover {
  color: var(--semantic-color-text-secondary);
}
.info-button:deep(svg) {
  width: 16px;
  height: 16px;
}

.info-popover-content {
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}
</style>
