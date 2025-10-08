<script setup>
import { computed } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { XMarkIcon } from '@heroicons/vue/24/solid';

const uiStore = useUiStore();
const imageUrl = computed(() => uiStore.lightboxImageUrl);

const close = () => {
  uiStore.closeLightbox();
};

// Close on escape key press
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && imageUrl.value) {
    close();
  }
});
</script>

<template>
  <transition name="lightbox-fade">
    <div v-if="imageUrl" class="lightbox-overlay" @click.self="close">
      <button class="close-button" @click="close">
        <XMarkIcon />
      </button>
      <div class="lightbox-content">
        <img :src="imageUrl" class="lightbox-image" @click.stop />
      </div>
    </div>
  </transition>
</template>

<style scoped>
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--semantic-layer-z-index-modal);
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.close-button svg {
  width: 32px;
  height: 32px;
}

.lightbox-content {
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-image {
  display: block;
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain; /* Ensures the image is fully visible within the container */
  border-radius: var(--semantic-border-radius-container);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

/* Transition styles */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.3s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}
</style>