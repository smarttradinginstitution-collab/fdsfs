<template>
  <div class="rule-group-creator">
    <BaseInput
      v-model="groupName"
      placeholder="Enter group name..."
      ref="inputRef"
      @keyup.enter="onSave"
      @keyup.esc="onCancel"
    />
    <div class="actions">
      <BaseButton @click="onSave" :disabled="!groupName.trim()">Save</BaseButton>
      <BaseButton @click="onCancel" variant="secondary">Cancel</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const store = usePlaybookStore();
const route = useRoute();

const groupName = ref('');
const inputRef = ref(null);

const onSave = async () => {
  if (!groupName.value.trim()) return;

  await store.createRuleGroup({
    playbookId: route.params.id,
    name_group: groupName.value,
  });

  // The store action will refresh the list and hide the creator
  store.setCreatingGroup(false);
};

const onCancel = () => {
  store.setCreatingGroup(false);
};

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<style scoped>
.rule-group-creator {
  background-color: var(--semantic-color-surface-primary);
  border: 1px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>