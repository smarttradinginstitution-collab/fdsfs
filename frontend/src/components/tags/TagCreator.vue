<template>
  <div class="tag-creator">
    <BaseInput
      v-model="tagName"
      placeholder="Enter new tag name..."
      ref="inputRef"
    />
    <ColorSelector v-model="tagColor" />
    <div class="actions">
      <BaseButton @click="onSave" :disabled="!tagName.trim()" :loading="isSaving">Save</BaseButton>
      <BaseButton @click="onCancel" variant="secondary">Cancel</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, computed } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';

const props = defineProps({
  groupId: {
    type: String,
    required: true,
  },
});

const store = useTagsStore();
const isSaving = computed(() => store.isSaving);

const tagName = ref('');
const tagColor = ref('#4A90E2'); // Default color
const inputRef = ref(null);

const onSave = async () => {
  if (!tagName.value.trim()) return;

  try {
    await store.createTag({
      name: tagName.value,
      color: tagColor.value,
      group_id: props.groupId,
    });
    // The store action will refresh the list and hide the creator
    store.setCreatingTagInGroup(null);
  } catch (e) {
    console.error("Failed to save tag from creator:", e);
  }
};

const onCancel = () => {
  store.setCreatingTagInGroup(null);
};

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<style scoped>
.tag-creator {
  padding: var(--semantic-size-inset-md);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-interactive);
  margin-top: var(--semantic-size-stack-sm);
}

.actions {
  display: flex;
  gap: var(--semantic-size-stack-sm);
  margin-left: auto; /* Push actions to the right */
}
</style>