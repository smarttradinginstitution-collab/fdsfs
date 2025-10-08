<template>
  <div class="group-creator">
    <BaseInput
      v-model="groupName"
      placeholder="Enter new group name..."
      ref="inputRef"
      @keyup.enter="onSave"
      @keyup.esc="onCancel"
    />
    <div class="actions">
      <BaseButton @click="onSave" :disabled="!groupName.trim()" :loading="isSaving">Save</BaseButton>
      <BaseButton @click="onCancel" variant="secondary">Cancel</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const store = useTagsStore();
const isSaving = computed(() => store.isSaving);

const groupName = ref('');
const inputRef = ref(null);

const onSave = async () => {
  if (!groupName.value.trim()) return;

  try {
    await store.createTagGroup({
      name: groupName.value,
    });
    // The store action will refresh the list, we just need to hide the creator
    store.setCreatingGroup(false);
  } catch (e) {
    // Error is handled in the store, but we log it here for debugging
    console.error("Failed to save group from creator:", e);
  }
};

const onCancel = () => {
  store.setCreatingGroup(false);
};

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<style scoped>
.group-creator {
  background-color: var(--semantic-color-surface-primary);
  border: 1px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  margin-bottom: var(--semantic-size-spacing-lg);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>