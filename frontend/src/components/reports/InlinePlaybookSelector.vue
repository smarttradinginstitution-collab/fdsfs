<script setup>
import { computed, onMounted } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseButton from '@/components/ui/BaseButton.vue';

const emit = defineEmits(['select', 'cancel']);

const playbookStore = usePlaybookStore();
const playbooks = computed(() => playbookStore.allPlaybooks);
const isLoading = computed(() => playbookStore.isLoading);

onMounted(() => {
  playbookStore.fetchPlaybooks();
});

const selectPlaybook = (playbookId) => {
  emit('select', playbookId);
};
</script>

<template>
  <div class="inline-playbook-selector">
    <div v-if="isLoading" class="loading-state">Loading playbooks...</div>
    <div v-else class="playbook-list">
      <div
        v-for="playbook in playbooks"
        :key="playbook.id"
        class="playbook-item"
        @click="selectPlaybook(playbook.id)"
      >
        {{ playbook.title }}
      </div>
    </div>
    <div class="actions">
      <BaseButton @click="$emit('cancel')" variant="secondary">Cancel</BaseButton>
    </div>
  </div>
</template>

<style scoped>
.inline-playbook-selector {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-md, 1rem);
  padding: var(--semantic-size-inset-md, 1rem);
  border: 1px solid var(--semantic-color-border-default, #e5e7eb);
  border-radius: var(--semantic-border-radius-container, 0.375rem);
  background-color: var(--semantic-color-surface-secondary, #f3f4f6);
}

.playbook-list {
  display: flex;
  flex-direction: column;
}

.playbook-item {
  padding: var(--semantic-size-inset-sm, 0.5rem) var(--semantic-size-inset-md, 1rem);
  cursor: pointer;
  border-radius: var(--semantic-border-radius-interactive, 0.25rem);
  font: var(--semantic-font-style-body-md, 1rem);
  color: var(--semantic-color-text-primary, #1f2937);
}

.playbook-item:hover {
  background-color: var(--semantic-color-surface-hover, #e5e7eb);
}

.actions {
  display: flex;
  justify-content: flex-end;
}
</style>