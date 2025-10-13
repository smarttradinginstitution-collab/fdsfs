<script setup>
import { computed, onMounted, onUnmounted } from 'vue';
import { XMarkIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  images: {
    type: Array,
    required: true,
  },
  currentIndex: {
    type: Number,
    required: true,
  },
  show: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'next', 'prev']);

const currentImage = computed(() => props.images[props.currentIndex]);

const close = () => {
  emit('close');
};

const next = () => {
  emit('next');
};

const prev = () => {
  emit('prev');
};

const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    close();
  }
  if (e.key === 'ArrowRight') {
    next();
  }
  if (e.key === 'ArrowLeft') {
    prev();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <transition name="fade">
    <div v-if="show" class="lightbox-overlay" @click.self="close">
      <button class="close-button" @click="close">
        <XMarkIcon />
      </button>

      <button class="nav-button prev" @click.stop="prev">
        <ChevronLeftIcon />
      </button>

      <div class="image-container">
        <transition name="slide" mode="out-in">
          <img :key="currentImage.id" :src="currentImage.url" :alt="currentImage.description || 'Lightbox image'" class="lightbox-image" />
        </transition>
      </div>

      <button class="nav-button next" @click.stop="next">
        <ChevronRightIcon />
      </button>
    </div>
  </transition>
</template>

<style lang="scss" scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.2s ease-out;
}
.slide-enter-from {
  opacity: 0;
  transform: scale(0.95);
}
.slide-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: var(--semantic-border-radius-container);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.close-button, .nav-button {
  position: absolute;
  background: rgba(30, 30, 30, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;

  &:hover {
    background: rgba(50, 50, 50, 0.8);
  }
}

.close-button {
  top: 2rem;
  right: 2rem;
  width: 48px;
  height: 48px;

  svg {
    width: 28px;
    height: 28px;
  }
}

.nav-button {
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;

  svg {
    width: 32px;
    height: 32px;
  }

  &.prev {
    left: 2rem;
  }

  &.next {
    right: 2rem;
  }
}
</style>