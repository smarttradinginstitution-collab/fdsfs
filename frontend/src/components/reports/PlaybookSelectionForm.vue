<script setup>
import { ref, onMounted, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseButton from '@/components/ui/BaseButton.vue';

const emit = defineEmits(['assign', 'cancel']);

const playbookStore = usePlaybookStore();
const selectedPlaybookId = ref(null);

const playbooks = computed(() => playbookStore.playbooks);
const isLoading = computed(() => playbookStore.isLoading);

const handleAssign = () => {
  if (selectedPlaybookId.value) {
    emit('assign', selectedPlaybookId.value);
  }
};

const handleCancel = () => {
  emit('cancel');
};

onMounted(() => {
  playbookStore.fetchPlaybooks();
});
</script>

<template>
  <div class="selection-form">
    <h3 class="form-title">Select a Playbook</h3>
    <div v-if="isLoading" class="loading-state">
      <p>Loading playbooks...</p>
    </div>
    <div v-else-if="playbooks.length === 0" class="empty-state">
      <p>No playbooks found. <router-link :to="{ name: 'playbooks' }">Create one</router-link>.</p>
    </div>
    <div v-else class="playbook-list">
      <label v-for="playbook in playbooks" :key="playbook.id" class="playbook-item">
        <input type="radio" :value="playbook.id" v-model="selectedPlaybookId" name="playbook" />
        <span class="playbook-title">{{ playbook.title }}</span>
        <span class="playbook-description">{{ playbook.description }}</span>
      </label>
    </div>
    <div class="form-actions">
      <BaseButton @click="handleCancel" variant="secondary" size="small">Cancel</BaseButton>
      <BaseButton @click="handleAssign" :disabled="!selectedPlaybookId" size="small" class="assign-button">Assign</BaseButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.selection-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-lg, 1.5rem);
  padding: var(--semantic-size-inset-md, 1rem);
  border: 1px solid var(--semantic-color-border-default, #e0e0e0);
  border-radius: var(--semantic-border-radius-container, 8px);
}

.form-title {
  font: var(--semantic-font-style-heading-md, 1.25rem);
  color: var(--semantic-color-text-primary, #000);
  margin: 0;
}

.loading-state,
.empty-state {
  padding: var(--semantic-size-inset-lg, 1.5rem);
  text-align: center;
  color: var(--semantic-color-text-secondary, #666);
}

.playbook-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-md, 1rem);
  max-height: 600px;
  overflow-y: auto;
}

.playbook-item {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: var(--semantic-size-gap-md, 1rem);
  padding: var(--semantic-size-inset-md, 1rem);
  border-radius: var(--semantic-border-radius-interactive, 6px);
  border: 1px solid var(--semantic-color-border-default, #e0e0e0);
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;

  &:hover {
    background-color: var(--semantic-color-surface-secondary, #f9f9f9);
  }

  input[type="radio"] {
    grid-row: 1 / span 2;
    margin: 0;
  }

  .playbook-title {
    font-weight: bold;
    color: var(--semantic-color-text-primary, #000);
    font-size: 0.9rem;
  }

  .playbook-description {
    grid-column: 2;
    font-size: 0.8rem;
    color: var(--semantic-color-text-secondary, #666);
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-gap-md, 1rem);
  margin-top: var(--semantic-size-gap-md, 1rem);
}

.assign-button {
  background-color: rgba(76, 175, 80, 0.6);
  color: white;
  border-color: transparent;
}

.assign-button:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.8);
}

.assign-button:disabled {
  background-color: rgba(76, 175, 80, 0.3);
  cursor: not-allowed;
}
</style>