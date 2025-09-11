<script setup>
import { ref } from 'vue';
import InfoIcon from '../icons/InfoIcon.vue';
import IconButton from './IconButton.vue';

const isOverlayVisible = ref(false);
</script>

<template>
  <div
    class="header-info-container"
    @mouseenter="isOverlayVisible = true"
    @mouseleave="isOverlayVisible = false"
  >
    <!-- Default Header Content -->
    <div class="title-container">
      <slot name="title"></slot>
      <InfoIcon class="title-icon" />
    </div>

    <!-- Overlay Content -->
    <div v-if="isOverlayVisible" class="info-overlay">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<style scoped>
.header-info-container {
  width: 100%;
  position: relative;
}

.title-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  width: 100%;
}

.title-icon {
  width: 16px;
  height: 16px;
  color: var(--semantic-color-text-tertiary);
  flex-shrink: 0;
}

.info-overlay {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  width: 100%;
  height: 100%;
  background-color: var(--semantic-color-surface-primary);
  z-index: 20;
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--semantic-size-stack-xs);
  border-radius: var(--semantic-border-radius-surface);
}
</style>
