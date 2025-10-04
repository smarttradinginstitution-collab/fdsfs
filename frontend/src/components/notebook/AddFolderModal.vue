<template>
  <BaseModal :show="isOpen" @close="$emit('close')">
    <template #header>
      <h2 class="text-lg font-semibold">Add New Folder</h2>
    </template>

    <div class="form-container">
      <BaseInput
        v-model="folderName"
        label="Folder Name"
        placeholder="e.g. Trade Ideas"
        :error-message="errorMessage"
      />

      <div class="color-selection-section">
        <label class="label">Folder Color</label>
        <ColorSelector v-model="folderColor" />
      </div>
    </div>

    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="secondary" @click="$emit('close')">Cancel</BaseButton>
        <BaseButton variant="primary" @click="handleCreate" :disabled="!isFormValid">Save</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue';
import BaseModal from '../ui/BaseModal.vue';
import BaseInput from '../ui/BaseInput.vue';
import BaseButton from '../ui/BaseButton.vue';
import ColorSelector from '../ui/ColorSelector.vue';

defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'create']);

const folderName = ref('');
const folderColor = ref('#4A90E2'); // Default color from ColorSelector
const errorMessage = ref('');

const isFormValid = computed(() => folderName.value.trim() !== '');

const handleCreate = () => {
  if (!isFormValid.value) {
    errorMessage.value = 'Folder name cannot be empty.';
    return;
  }
  errorMessage.value = '';
  emit('create', { name: folderName.value, color: folderColor.value });
};
</script>

<style lang="scss" scoped>
.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 350px;
}

.color-selection-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.label {
  font-weight: 500;
  color: var(--semantic-color-text-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  width: 100%;
}
</style>