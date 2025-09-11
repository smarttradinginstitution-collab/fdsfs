<script setup>
import { ref, onMounted } from 'vue';
import HoverPopover from './HoverPopover.vue';
import PopoverMenu from './PopoverMenu.vue';
import IconButton from './IconButton.vue';
import InfoIcon from '../icons/InfoIcon.vue';

defineProps({
  ariaLabel: {
    type: String,
    required: true,
  },
});

const isTouchDevice = ref(false);

onMounted(() => {
  isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
});
</script>

<template>
  <PopoverMenu v-if="isTouchDevice">
    <template #trigger="{ toggle }">
      <IconButton @click="toggle" :aria-label="ariaLabel" size="small" class="info-button">
        <InfoIcon />
      </IconButton>
    </template>
    <template #content>
      <div class="info-popover-content">
        <slot></slot>
      </div>
    </template>
  </PopoverMenu>

  <HoverPopover v-else>
    <template #trigger>
      <IconButton :aria-label="ariaLabel" size="small" class="info-button" tabindex="-1">
        <InfoIcon />
      </IconButton>
    </template>
    <template #content>
      <div class="info-popover-content">
        <slot></slot>
      </div>
    </template>
  </HoverPopover>
</template>

<style scoped>
.info-button {
  color: var(--semantic-color-text-tertiary);
}
.info-button:hover {
  color: var(--semantic-color-text-secondary);
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
