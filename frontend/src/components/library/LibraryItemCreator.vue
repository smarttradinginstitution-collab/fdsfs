<template>
  <div class="item-creator">
    <BaseInput
      v-model="itemName"
      placeholder="Enter new item name..."
      ref="inputRef"
      @keyup.enter="onSave"
      @keyup.esc="onCancel"
    />
    <BaseSelect
      v-if="isGrouped"
      v-model="selectedGroupId"
      :options="groups"
      placeholder="Select a group"
      label="Group"
    />
    <ColorSelector v-model="itemColor" />
    <div class="actions">
      <BaseButton @click="onSave" :disabled="!itemName.trim()" :is-loading="isSaving">Save</BaseButton>
      <BaseButton @click="onCancel" variant="secondary">Cancel</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';

const props = defineProps({
  isSaving: {
    type: Boolean,
    default: false,
  },
  initialName: {
    type: String,
    default: '',
  },
  initialColor: {
    type: String,
    default: '#4A90E2',
  },
  isGrouped: {
    type: Boolean,
    default: false,
  },
  groups: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['save', 'cancel']);

const itemName = ref('');
const itemColor = ref('#4A90E2');
const selectedGroupId = ref(null);
const inputRef = ref(null);

const onSave = () => {
  if (!itemName.value.trim()) return;
  const data = { name: itemName.value, color: itemColor.value };
  if (props.isGrouped) {
    if (!selectedGroupId.value) {
      // TODO: Add user feedback about needing to select a group
      console.error("Please select a group for the new impact.");
      return;
    }
    data.group_id = selectedGroupId.value;
  }
  emit('save', data);
};

const onCancel = () => {
  emit('cancel');
};

onMounted(() => {
  itemName.value = props.initialName;
  itemColor.value = props.initialColor;
  inputRef.value?.focus();
});
</script>

<style scoped>
.item-creator {
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--semantic-size-stack-md);
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-interactive);
  margin-top: var(--semantic-size-stack-sm);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>