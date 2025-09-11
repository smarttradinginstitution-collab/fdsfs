<script setup>
import { ref } from 'vue';

const isHovering = ref(false);

const showPopover = () => {
  isHovering.value = true;
};

const hidePopover = () => {
  isHovering.value = false;
};
</script>

<template>
  <div
    class="popover-container"
    @mouseenter="showPopover"
    @mouseleave="hidePopover"
  >
    <slot name="trigger"></slot>
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isHovering" class="popover-panel">
        <slot name="content"></slot>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.popover-container {
  position: relative;
  display: inline-block;
}

.popover-panel {
  position: absolute;
  /* Position it relative to the trigger */
  left: 50%;
  transform: translateX(-50%);
  top: 100%;
  margin-top: var(--base-size-spacing-2);
  width: max-content;
  max-width: 280px; /* Sensible max-width */
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
  z-index: 10;
}
</style>
