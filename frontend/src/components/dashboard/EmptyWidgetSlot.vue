<template>
  <div class="empty-widget-slot" @click="$emit('click')">
    <p>Click to add widget</p>
  </div>
</template>

<script setup>
defineEmits(['click']);
</script>

<style scoped>
.empty-widget-slot {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px dashed var(--color-border-default);
  border-radius: var(--semantic-border-radius-lg);
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.empty-widget-slot:hover {
  background-color: var(--color-background-muted);
}

.empty-widget-slot p {
  color: var(--color-text-subtle);
  font-weight: var(--font-weight-semibold);
}
</style>
