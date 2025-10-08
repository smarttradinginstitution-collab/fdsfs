<template>
  <BaseModal :show="show" @close="$emit('close')" class="z-50">
    <template #header>
      <h2 class="text-lg font-semibold">{{ modalTitle }}</h2>
    </template>

    <template #default>
      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            v-model="groupName"
            label="Group Name"
            placeholder="e.g., Strategies, Market Conditions"
            required
            :error="validationError"
          />
        </div>
      </form>
    </template>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton variant="secondary" @click="$emit('close')">Cancel</BaseButton>
        <BaseButton @click="handleSubmit" :loading="isSaving">
          {{ isEditing ? 'Save Changes' : 'Create Group' }}
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

const props = defineProps({
  show: Boolean,
  group: {
    type: Object,
    default: null,
  },
  isSaving: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['close', 'save']);

const groupName = ref('');
const validationError = ref('');

const isEditing = computed(() => !!props.group);
const modalTitle = computed(() => isEditing.value ? 'Edit Tag Group' : 'Create New Tag Group');

watch(() => props.group, (newGroup) => {
  if (newGroup) {
    groupName.value = newGroup.name;
  } else {
    groupName.value = ''; // Reset when no group is being edited (i.e., for creation)
  }
  validationError.value = '';
}, { immediate: true });

const handleSubmit = () => {
  if (!groupName.value.trim()) {
    validationError.value = 'Group name is required.';
    return;
  }
  validationError.value = '';

  const payload = {
    name: groupName.value,
  };

  // If editing, include the group ID in the payload for the store action
  if (isEditing.value) {
    emit('save', { ...payload, id: props.group.id });
  } else {
    emit('save', payload);
  }
};
</script>