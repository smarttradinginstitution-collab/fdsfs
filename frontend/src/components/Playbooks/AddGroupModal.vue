<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3 class="modal-title">Add New Group</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <BaseInput
            label="Group Name"
            v-model="groupName"
            placeholder="e.g., Entry Rules"
            required
          />
        </div>
        <div class="modal-actions">
          <BaseButton type="button" variant="secondary" @click="$emit('close')">Cancel</BaseButton>
          <BaseButton type="submit" variant="primary">Add Group</BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const emit = defineEmits(['close', 'add-group']);

const groupName = ref('');

const handleSubmit = () => {
  if (groupName.value) {
    emit('add-group', groupName.value);
  }
};
</script>

<style scoped>
/* Reusing styles from AddBlockModal for consistency */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6); display: flex;
    justify-content: center; align-items: center; z-index: 1001; /* Higher z-index */
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
.modal-actions {
    display: flex; justify-content: flex-end; gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-lg);
}
</style>
