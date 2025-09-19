<script setup>
import { ref, computed } from 'vue';
import BaseModal from './BaseModal.vue';
import BaseButton from './BaseButton.vue';
import BaseInput from './BaseInput.vue';

const props = defineProps({
  show: Boolean,
  title: String,
  confirmationWord: String,
});

const emit = defineEmits(['close', 'confirm']);

const confirmationInput = ref('');

const isConfirmed = computed(() => {
  return confirmationInput.value === props.confirmationWord;
});

function confirm() {
  if (isConfirmed.value) {
    emit('confirm');
  }
}

function close() {
  confirmationInput.value = '';
  emit('close');
}
</script>

<template>
  <BaseModal :show="show" @close="close">
    <template #header>
      <h2 class="text-xl font-bold">{{ title }}</h2>
    </template>
    <template #default>
      <slot></slot>
      <div class="mt-4">
        <label for="confirmation-input" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          To confirm, please type "<strong>{{ confirmationWord }}</strong>" below:
        </label>
        <BaseInput
          id="confirmation-input"
          v-model="confirmationInput"
          class="mt-1 block w-full"
        />
      </div>
    </template>
    <template #footer>
      <BaseButton @click="close" variant="secondary">Cancel</BaseButton>
      <BaseButton @click="confirm" :disabled="!isConfirmed" variant="secondary">
        Confirm
      </BaseButton>
    </template>
  </BaseModal>
</template>
