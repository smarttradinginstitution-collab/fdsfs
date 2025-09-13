<script setup>
import { ref } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import apiClient from '@/services/api';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';

const uiStore = useUiStore();

const mfaStep = ref('start'); // 'start', 'enroll', 'verify'
const qrCodeSvg = ref('');
const verificationCode = ref('');
const error = ref(null);
const isLoading = ref(false);

async function handleEnableMfa() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.post('/api/v1/auth/mfa/enroll');
    qrCodeSvg.value = response.data.qr_code_svg;
    // We need the factor_id for the verification step
    mfaStep.value = 'verify';
    localStorage.setItem('mfa_factor_id', response.data.factor_id);
  } catch (err) {
    error.value = 'Failed to start MFA enrollment. Please try again.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function handleVerifyMfa() {
  isLoading.value = true;
  error.value = null;
  const factorId = localStorage.getItem('mfa_factor_id');
  if (!factorId) {
      error.value = "Factor ID not found. Please start over.";
      mfaStep.value = 'start';
      return;
  }
  try {
    await apiClient.post('/api/v1/auth/mfa/verify', {
      factor_id: factorId,
      code: verificationCode.value,
    });
    uiStore.showNotification({ message: 'MFA enabled successfully!', type: 'success' });
    localStorage.removeItem('mfa_factor_id');
    closeModal();
  } catch (err) {
    error.value = 'Invalid verification code. Please try again.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

function closeModal() {
  uiStore.closeSettingsModal();
  // Reset state when closing
  mfaStep.value = 'start';
  qrCodeSvg.value = '';
  verificationCode.value = '';
  error.value = null;
  localStorage.removeItem('mfa_factor_id');
}
</script>

<template>
  <BaseModal
    :is-open="uiStore.isSettingsModalOpen"
    title="Settings"
    @close="closeModal"
  >
    <div v-if="mfaStep === 'start'">
      <h3 class="settings-header">Multi-Factor Authentication</h3>
      <p class="settings-description">
        Add an extra layer of security to your account.
      </p>
      <BaseButton @click="handleEnableMfa" :disabled="isLoading">
        {{ isLoading ? 'Loading...' : 'Enable MFA' }}
      </BaseButton>
    </div>

    <div v-if="mfaStep === 'verify'">
      <h3 class="settings-header">Set up MFA</h3>
      <p class="settings-description">
        Scan the QR code with your authenticator app, then enter the 6-digit code below.
      </p>
      <div class="qr-code" v-html="qrCodeSvg"></div>
      <form @submit.prevent="handleVerifyMfa">
        <BaseInput
          v-model="verificationCode"
          label="Verification Code"
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="6"
          required
        />
        <BaseButton type="submit" :disabled="isLoading" class="mt-4">
          {{ isLoading ? 'Verifying...' : 'Verify & Enable' }}
        </BaseButton>
      </form>
    </div>

    <p v-if="error" class="error-message">{{ error }}</p>
  </BaseModal>
</template>

<style scoped>
.settings-header {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.settings-description {
  margin-bottom: 1.5rem;
  color: var(--semantic-color-text-secondary);
}
.qr-code {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: white;
  display: inline-block;
  border-radius: var(--semantic-border-radius-default);
}
.error-message {
  color: var(--semantic-color-text-danger);
  margin-top: 1rem;
}
.mt-4 {
    margin-top: 1rem;
}
</style>
