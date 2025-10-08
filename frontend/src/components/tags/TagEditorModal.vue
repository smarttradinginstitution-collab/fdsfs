<template>
  <BaseModal :show="show" @close="$emit('close')" class="z-50">
    <template #header>
      <h2 class="text-lg font-semibold">{{ modalTitle }}</h2>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <BaseInput
        v-model="tagName"
        label="Tag Name"
        placeholder="e.g., Breakout, Reversal"
        required
        :error="validationError"
      />

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tag Color</label>
        <ColorSelector v-model="tagColor" />
      </div>
    </form>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton variant="secondary" @click="$emit('close')">Cancel</BaseButton>
        <BaseButton @click="handleSubmit" :loading="isSaving">
          {{ isEditing ? 'Save Changes' : 'Create Tag' }}
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';

const props = defineProps({
  show: Boolean,
  tag: {
    type: Object,
    default: null,
  },
  groupId: {
    type: String,
    default: null,
  },
  isSaving: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['close', 'save']);

const tagName = ref('');
const tagColor = ref('#4A90E2'); // Default color
const validationError = ref('');

const isEditing = computed(() => !!props.tag);
const modalTitle = computed(() => isEditing.value ? 'Edit Tag' : 'Create New Tag');

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset form when modal opens
    tagName.value = props.tag ? props.tag.name : '';
    tagColor.value = props.tag ? props.tag.color : '#4A90E2';
    validationError.value = '';
  }
});

const handleSubmit = () => {
  if (!tagName.value.trim()) {
    validationError.value = 'Tag name is required.';
    return;
  }
  validationError.value = '';

  const payload = {
    name: tagName.value,
    color: tagColor.value,
    tags_group_id: props.groupId,
  };

  if (isEditing.value) {
    emit('save', { ...payload, id: props.tag.id });
  } else {
    emit('save', payload);
  }
};
</script>