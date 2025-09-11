<script setup>
import HoverPopover from './HoverPopover.vue';
import IconButton from './IconButton.vue';
import InfoIcon from '../icons/InfoIcon.vue';
</script>

<template>
  <HoverPopover>
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
</template>

<style scoped>
/* Styles are scoped to this component, making it self-contained. */
.info-button {
  color: var(--semantic-color-text-tertiary);
  /* We use :deep to style the SVG inside the IconButton component */
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
