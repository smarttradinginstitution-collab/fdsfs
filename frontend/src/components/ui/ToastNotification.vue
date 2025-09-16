<script setup>
import { computed } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import SuccessIcon from '@/components/icons/SuccessIcon.vue';
import ErrorIcon from '@/components/icons/ErrorIcon.vue';

const uiStore = useUiStore();

const notification = computed(() => uiStore.notification);

const notificationClass = computed(() => {
  return {
    'toast-notification': true,
    'toast-notification--success': notification.value.type === 'success',
    'toast-notification--error': notification.value.type === 'error',
    'toast-notification--show': notification.value.show,
  };
});
</script>

<template>
  <transition name="toast">
    <div v-if="notification.show" :class="notificationClass">
      <div class="toast-notification__icon">
        <SuccessIcon v-if="notification.type === 'success'" />
        <ErrorIcon v-if="notification.type === 'error'" />
      </div>
      <p class="toast-notification__message">{{ notification.message }}</p>
    </div>
  </transition>
</template>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: white;
  z-index: 1000;
  transform: translateY(200%);
  transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-notification--show {
    transform: translateY(0);
}

.toast-notification--success {
  background-color: var(--semantic-color-feedback-positive-background);
  color: var(--semantic-color-text-on-brand);
}

.toast-notification--error {
  background-color: var(--semantic-color-feedback-negative-background);
  color: var(--semantic-color-text-on-brand);
}

.toast-notification__icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-notification__icon svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: currentColor;
}

.toast-notification__message {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

/* Transition styles */
.toast-enter-active,
.toast-leave-active {
  transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-enter-from,
.toast-leave-to {
  transform: translateY(200%);
}
</style>
