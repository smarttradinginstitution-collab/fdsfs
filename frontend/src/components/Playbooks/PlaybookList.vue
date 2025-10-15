<template>
  <div v-if="isLoading" class="loading-state">
    <p>Loading playbooks...</p>
  </div>
  <div v-else-if="playbooks.length === 0" class="empty-state">
    <p>No playbooks found. Start by creating one!</p>
  </div>
  <div v-else :class="['playbook-list', layoutClass]">
    <PlaybookCard
      v-for="playbook in playbooks"
      :key="playbook.id"
      :playbook="playbook"
      :layout="layout"
    />
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue';
import PlaybookCard from './PlaybookCard.vue';

const props = defineProps({
  playbooks: {
    type: Array,
    required: true,
  },
  layout: {
    type: String,
    default: 'grid', // 'grid' or 'list'
  },
  isLoading: {
    type: Boolean,
    default: false,
  }
});

const layoutClass = computed(() => {
  return props.layout === 'grid' ? 'layout-grid' : 'layout-list';
});
</script>

<style scoped>
.loading-state, .empty-state {
  text-align: center;
  padding: 4rem;
  color: var(--color-text-secondary);
}

.playbook-list {
  display: grid;
  gap: var(--semantic-size-stack-lg);
}

/* Grid layout for desktop */
.layout-grid {
  /* As per user request, max 2 columns */
  grid-template-columns: repeat(2, 1fr);
}

/* List layout for desktop */
.layout-list {
  grid-template-columns: 1fr;
}

/* Responsive behavior for mobile */
@media (max-width: 1024px) {
  .layout-grid, .layout-list {
    /* Always force single column on mobile */
    grid-template-columns: 1fr;
  }
}
</style>