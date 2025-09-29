<template>
  <div class="playbook-controls">
    <div class="left-controls">
      <!-- Search bar can be added here later if needed -->
    </div>
    <div class="right-controls">
      <div class="layout-switchers">
        <button @click="setLayout('grid')" :class="{ active: currentLayout === 'grid' }">Grid</button>
        <button @click="setLayout('list')" :class="{ active: currentLayout === 'list' }">List</button>
      </div>
      <button class="create-button">Create New Playbook</button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(['update:layout']);

const currentLayout = ref('grid');

function setLayout(layout) {
  currentLayout.value = layout;
  emit('update:layout', layout);
}
</script>

<style scoped>
.playbook-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.right-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.layout-switchers {
  display: flex;
  border: 1px solid #ccc;
  border-radius: var(--semantic-border-radius-interactive);
  overflow: hidden;
}

.layout-switchers button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: transparent;
  cursor: pointer;
}

.layout-switchers button.active {
  background-color: #e0e0e0;
}

.create-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
}

/* Responsive behavior */
@media (max-width: 1024px) {
  .layout-switchers {
    display: none;
  }
}
</style>