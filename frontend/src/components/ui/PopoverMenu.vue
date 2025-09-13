<script setup>
import { ref, watch } from 'vue';
import { onClickOutside } from '@vueuse/core';

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close']);

const isOpen = ref(props.show);
const popoverRef = ref(null);

watch(() => props.show, (newValue) => {
  isOpen.value = newValue;
});

const toggle = () => {
  isOpen.value = !isOpen.value;
  if (!isOpen.value) {
    emit('close');
  }
};

const close = () => {
  if (isOpen.value) {
    isOpen.value = false;
    emit('close');
  }
};

onClickOutside(popoverRef, close);

// Expose the toggle function to the parent component
defineExpose({ toggle });
</script>

<template>
  <div class="popover-container" ref="popoverRef">
    <slot name="trigger" :toggle="toggle"></slot>
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isOpen" class="popover-panel">
        <slot name="content" :close="close"></slot>
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
  right: 0;
  margin-top: var(--base-size-spacing-2);
  width: max-content;
  max-width: 90vw;
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
  z-index: 10;
}
</style>
