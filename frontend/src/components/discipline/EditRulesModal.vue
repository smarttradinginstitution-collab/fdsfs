<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Edit Rules</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <p>Form to create, edit, and delete rules will go here.</p>
        <!-- Rule list and form will be implemented here -->
      </div>
      <div class="modal-footer">
        <button @click="close" class="btn-secondary">Cancel</button>
        <button @click="save" class="btn-primary">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
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
  background-color: rgba(0, 0, 0, 0.6);
  display: grid;
  place-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-container);
  padding: 2rem;
  width: 90%;
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h3 {
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  font-weight: 600;
}

.btn-secondary {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
  border: 1px solid var(--semantic-color-border-default);
  padding: 0.75rem 1.5rem;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  font-weight: 600;
}
</style>