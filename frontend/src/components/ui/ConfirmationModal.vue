<template>
  <BaseModal :show="show" @close="$emit('close')">
    <template #header>
      <h3 class="title">{{ title }}</h3>
    </template>

    <p class="message">{{ message }}</p>

    <template #footer>
      <div class="footer-actions">
        <BaseButton @click="$emit('close')" variant="secondary">Cancel</BaseButton>
        <BaseButton @click="$emit('confirm')" variant="danger">Confirm</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue';
import BaseButton from './BaseButton.vue';

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'Confirm Action',
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?',
  },
});

defineEmits(['close', 'confirm']);
</script>

<style scoped>
.title {
  font: var(--semantic-font-style-heading-h4);
  color: var(--semantic-color-text-primary);
}

.message {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  line-height: 1.5;
  margin: var(--semantic-size-stack-sm) 0;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  margin-top: var(--semantic-size-stack-lg);
}
</style>