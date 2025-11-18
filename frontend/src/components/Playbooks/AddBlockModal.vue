<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3 class="modal-title">Add New Content Block</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <BaseSelect
            label="Block Type"
            v-model="blockType"
            :options="blockTypeOptions"
            required
          />
          <p class="description">{{ selectedOptionDescription }}</p>
        </div>
        <div class="form-group">
          <BaseInput
            label="Block Title"
            v-model="title"
            placeholder="e.g., Entry Criteria"
            required
          />
        </div>
        <div class="modal-actions">
          <BaseButton type="button" variant="secondary" @click="$emit('close')">Cancel</BaseButton>
          <BaseButton type="submit" variant="primary">Add Block</BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const emit = defineEmits(['close', 'create-block']);

const blockType = ref('RULES');
const title = ref('');

const blockTypeOptions = [
  { value: 'THESIS', label: '📝 Narrative & Thesis', description: 'Explain the logic and context of the strategy.' },
  { value: 'RULES', label: '⚙️ Rules & Conditions', description: 'Set checklists, entry criteria, and objective rules.' },
  { value: 'GALLERY', label: '🖼️ Chart Gallery', description: 'Upload examples of ideal setups (A+) and traps.' },
];

const selectedOptionDescription = computed(() => {
  const selected = blockTypeOptions.find(opt => opt.value === blockType.value);
  return selected ? selected.description : '';
});

const handleSubmit = () => {
  if (blockType.value && title.value) {
    emit('create-block', {
      block_type: blockType.value,
      title: title.value,
    });
  }
};
</script>

<style scoped>
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6); display: flex;
    justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
    background-color: var(--semantic-color-surface-primary);
    padding: var(--semantic-size-inset-lg);
    border-radius: var(--semantic-border-radius-surface);
    width: 100%;
    max-width: 500px;
    display: flex; flex-direction: column; gap: var(--semantic-size-stack-lg);
}
.modal-title {
    font: var(--semantic-font-style-headline-md);
}
.form-group {
    margin-bottom: var(--semantic-size-stack-md);
}
.description {
    font: var(--semantic-font-style-body-sm);
    color: var(--semantic-color-text-subtle);
    margin-top: var(--semantic-size-stack-xs);
}
.modal-actions {
    display: flex; justify-content: flex-end; gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-lg);
}
</style>
