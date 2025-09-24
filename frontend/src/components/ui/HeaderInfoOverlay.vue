<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue';
import InfoIcon from '../icons/InfoIcon.vue';
import IconButton from './IconButton.vue';

defineProps({
  ariaLabel: {
    type: String,
    required: true,
  },
});

const isOverlayVisible = ref(false);
const overlayClasses = ref('');
const isMobileView = ref(false);
const iconButtonRef = ref(null);
let hideTimeout = null;

const MOBILE_BREAKPOINT = 640; // Corresponds to 'sm' breakpoint

const checkPositionAndSetClasses = async () => {
  if (!isOverlayVisible.value) return;

  isMobileView.value = window.innerWidth < MOBILE_BREAKPOINT;

  if (isMobileView.value) {
    overlayClasses.value = 'is-mobile-modal';
    return;
  }

  await nextTick();

  if (iconButtonRef.value?.$el) {
    const buttonRect = iconButtonRef.value.$el.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const overlayWidth = 300; // A reasonable estimate for the overlay's width
    const margin = 16; // Margin from the edge of the viewport

    if (buttonRect.right + overlayWidth > viewportWidth - margin) {
      overlayClasses.value = 'align-left';
    } else {
      overlayClasses.value = 'align-right';
    }
  }
};

const showOverlay = () => {
  if (hideTimeout) clearTimeout(hideTimeout);
  isOverlayVisible.value = true;
  checkPositionAndSetClasses();
};

const startHideTimeout = () => {
  hideTimeout = setTimeout(() => {
    isOverlayVisible.value = false;
  }, 300); // A slightly longer delay for better UX
};

onMounted(() => {
  window.addEventListener('resize', checkPositionAndSetClasses);
});
onUnmounted(() => {
  window.removeEventListener('resize', checkPositionAndSetClasses);
});
</script>

<template>
  <div class="header-info-container">
    <div class="title-container" :class="{ 'is-hidden': isOverlayVisible && !isMobileView }">
      <slot name="title"></slot>
      <IconButton
        ref="iconButtonRef"
        :aria-label="ariaLabel"
        size="small"
        class="info-button"
        @mouseenter="showOverlay"
        @mouseleave="startHideTimeout"
        @focus="showOverlay"
        @blur="startHideTimeout"
      >
        <InfoIcon />
      </IconButton>
    </div>

    <div
      v-if="isOverlayVisible"
      :class="['info-overlay', overlayClasses]"
      @mouseenter="showOverlay"
      @mouseleave="startHideTimeout"
    >
      <div v-if="isMobileView" class="mobile-modal-content">
        <slot name="content"></slot>
      </div>
      <slot v-else name="content"></slot>
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

.info-button {
  color: var(--semantic-color-text-tertiary);
  flex-shrink: 0;
}
.info-button:hover {
  color: var(--semantic-color-text-secondary);
}

.info-overlay {
  position: absolute;
  top: 0;
  background-color: var(--semantic-color-surface-primary);
  z-index: 20;
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--semantic-size-stack-xs);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-medium);
  width: 300px; /* Default width */
  visibility: hidden; /* Hide by default, show with classes */
  opacity: 0;
  transition: opacity 0.2s, visibility 0.2s;
}

.info-overlay.align-left,
.info-overlay.align-right,
.info-overlay.is-mobile-modal {
  visibility: visible;
  opacity: 1;
}

.info-overlay.align-right {
  left: 0;
}

.info-overlay.align-left {
  right: 0;
}

/* Mobile Modal Styles */
.info-overlay.is-mobile-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent backdrop */
  border-radius: 0;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--semantic-size-inset-lg);
}

.mobile-modal-content {
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-surface);
  width: 100%;
  max-width: 400px;
  box-shadow: var(--semantic-effect-shadow-elevation-high);
}
</style>
