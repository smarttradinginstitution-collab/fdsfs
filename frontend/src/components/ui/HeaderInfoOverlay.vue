<script setup>
import { ref } from 'vue';
import InfoIcon from '../icons/InfoIcon.vue';

const isOverlayVisible = ref(false);
let hideTimeout = null;

const showOverlay = () => {
  if (hideTimeout) clearTimeout(hideTimeout);
  isOverlayVisible.value = true;
};

const startHideTimeout = () => {
  hideTimeout = setTimeout(() => {
    isOverlayVisible.value = false;
  }, 100); // A small delay to allow moving the mouse between icon and panel
};
</script>

<template>
  <div class="header-info-container">
    <div class="title-container" :class="{ 'is-hidden': isOverlayVisible }">
      <slot name="title"></slot>
      <div
        class="icon-wrapper"
        @mouseenter="showOverlay"
        @mouseleave="startHideTimeout"
      >
        <InfoIcon class="title-icon" />
      </div>
    </div>

    <div
      v-if="isOverlayVisible"
      class="info-overlay"
      @mouseenter="showOverlay"
      @mouseleave="startHideTimeout"
    >
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
  justify-content: space-between;
  gap: var(--semantic-size-stack-sm);
  width: 100%;
  transition: visibility 0.1s, opacity 0.1s;
  visibility: visible;
  opacity: 1;
}

.title-container.is-hidden {
  visibility: hidden;
  opacity: 0;
}

.icon-wrapper {
  display: flex;
  align-items: center;
}

.title-icon {
  width: 16px;
  height: 16px;
  color: var(--semantic-color-text-tertiary);
  flex-shrink: 0;
}

.info-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  /* Use min-height to ensure it's at least as tall as the header */
  min-height: 100%;
  height: auto;
  background-color: var(--semantic-color-surface-primary);
  z-index: 20;
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--semantic-size-stack-xs);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}
</style>
