<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">Edit Rules</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <p>Form to create, edit, and delete rules will go here.</p>
        <!-- Rule list and form will be implemented here -->
      </div>
      <div class="modal-footer">
        <BaseButton @click="close" variant="secondary" size="medium">Cancel</BaseButton>
        <BaseButton @click="save" variant="primary" size="medium">Save Changes</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue';

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'save']);

function close() {
  emit('close');
}

function save() {
  // Save logic will be handled by the parent component
  emit('save');
  close();
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--semantic-color-overlay-background);
  display: grid;
  place-items: center;
  z-index: var(--semantic-layer-z-index-modal);
}

.modal-content {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-component-modal-padding-desktop);
  width: 90%;
  max-width: var(--semantic-size-component-modal-max-width-desktop);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-component-modal-gap-desktop);
}

.modal-title {
  font: var(--semantic-font-style-heading-lg);
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}

.modal-body {
    min-height: 200px; /* Placeholder height */
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  margin-top: var(--semantic-size-component-modal-gap-desktop);
}
</style>