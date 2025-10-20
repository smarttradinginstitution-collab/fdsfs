<template>
  <div ref="observerElement" class="lazy-load-trigger">
    <slot v-if="isVisible"></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const observerElement = ref(null);
const isVisible = ref(false);
let observer = null;

const props = defineProps({
  // Opzione per mantenere il componente montato dopo la prima visualizzazione
  unobserveOnVisible: {
    type: Boolean,
    default: true,
  },
  // Opzioni per l'IntersectionObserver
  options: {
    type: Object,
    default: () => ({
      root: null, // null significa il viewport
      rootMargin: '0px 0px 200px 0px', // Inizia a caricare 200px prima che l'elemento sia visibile
      threshold: 0, // Appena un pixel è visibile
    }),
  },
});

onMounted(() => {
  if (observerElement.value) {
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          isVisible.value = true;
          if (props.unobserveOnVisible) {
            observer.unobserve(observerElement.value);
          }
        }
      });
    }, props.options);
    observer.observe(observerElement.value);
  }
});

onUnmounted(() => {
  if (observer && observerElement.value) {
    observer.unobserve(observerElement.value);
  }
});
</script>

<style scoped>
.lazy-load-trigger {
  min-height: 1px; /* Assicura che l'elemento abbia una dimensione per essere osservato */
}
</style>
