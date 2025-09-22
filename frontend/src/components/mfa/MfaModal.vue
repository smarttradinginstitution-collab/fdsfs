<template>
  <BaseModal :show="modelValue" @close="$emit('update:modelValue', false)" title="Gestione MFA">
    <div v-if="mode === 'enroll'">
      <h3 class="modal-subtitle">Attiva Autenticazione a Due Fattori</h3>
      <div v-if="isLoading" class="loading-state">
        <LoadingSpinner />
        <p>Generazione del codice QR in corso...</p>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="enrollData" class="enroll-content">
        <p>1. Scansiona questo codice QR con la tua app di autenticazione.</p>
        <div class="qr-code" v-html="cleanedQrCode"></div>
        <p>2. Inserisci il codice a 6 cifre per completare l'attivazione.</p>
        <BaseInput
          v-model="otpCode"
          placeholder="123456"
          label="Codice di verifica"
          :disabled="isVerifying"
        />
        <BaseButton @click="handleVerifyAndEnable" :disabled="!otpCode || isVerifying">
          {{ isVerifying ? 'Verifica in corso...' : 'Verifica e Attiva' }}
        </BaseButton>
      </div>
    </div>

    <div v-if="mode === 'disable'">
      <h3 class="modal-subtitle">Disattiva Autenticazione a Due Fattori</h3>
      <p>Per confermare la disattivazione, inserisci un codice dalla tua app di autenticazione.</p>
      <div v-if="error" class="error-message">{{ error }}</div>
      <BaseInput
        v-model="otpCode"
        placeholder="123456"
        label="Codice di verifica"
        :disabled="isDisabling"
      />
      <BaseButton @click="handleDisable" :disabled="!otpCode || isDisabling" variant="danger">
        {{ isDisabling ? 'Disattivazione in corso...' : 'Conferma e Disattiva' }}
      </BaseButton>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import BaseModal from '../ui/BaseModal.vue';
import BaseButton from '../ui/BaseButton.vue';
import BaseInput from '../ui/BaseInput.vue';
import LoadingSpinner from '../ui/LoadingSpinner.vue';

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, required: true, validator: (v) => ['enroll', 'disable'].includes(v) },
});
const emit = defineEmits(['update:modelValue', 'success']);

const authStore = useAuthStore();
const otpCode = ref('');
const enrollData = ref(null);
const unverifiedFactorId = ref(null); // Traccia il fattore creato ma non ancora verificato
const isLoading = ref(false);
const isVerifying = ref(false);
const isDisabling = ref(false);
const error = ref('');

const cleanedQrCode = computed(() => {
  if (!enrollData.value?.qr_code) return '';
  return enrollData.value.qr_code.replace(/\\"/g, '"').replace(/\\n/g, '');
});

async function fetchEnrollmentDetails() {
  isLoading.value = true;
  error.value = '';
  try {
    const data = await authStore.enrollMfa();
    enrollData.value = data;
    unverifiedFactorId.value = data.factor_id; // Salva l'ID del fattore non verificato
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore durante la generazione del QR code.';
  } finally {
    isLoading.value = false;
  }
}

async function handleVerifyAndEnable() {
  isVerifying.value = true;
  error.value = '';
  try {
    await authStore.verifyAndEnableMfa(enrollData.value.factor_id, enrollData.value.challenge_id, otpCode.value);
    unverifiedFactorId.value = null; // Il fattore è stato verificato, non serve più pulirlo
    emit('success', 'MFA attivata con successo!');
    emit('update:modelValue', false);
  } catch (e) {
    error.value = 'Codice di verifica non valido.';
  } finally {
    isVerifying.value = false;
  }
}

async function handleDisable() {
  isDisabling.value = true;
  error.value = '';
  try {
    await authStore.disableMfa(otpCode.value);
    emit('success', 'MFA disattivata con successo!');
    emit('update:modelValue', false);
  } catch (e) {
    error.value = 'Disattivazione fallita. Il codice OTP è valido?';
  } finally {
    isDisabling.value = false;
  }
}

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    // La modale si sta aprendo
    otpCode.value = '';
    error.value = '';
    enrollData.value = null;
    unverifiedFactorId.value = null;
    if (props.mode === 'enroll') {
      fetchEnrollmentDetails();
    }
  } else {
    // La modale si sta chiudendo
    // Se stavamo facendo l'enroll e abbiamo un fattore non verificato, puliamolo.
    if (props.mode === 'enroll' && unverifiedFactorId.value) {
      authStore.unenrollMfa(unverifiedFactorId.value);
    }
  }
});
</script>

<style scoped>
.modal-subtitle { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }
.loading-state, .enroll-content, .disable-content { display: flex; flex-direction: column; gap: 1rem; }
.qr-code { align-self: center; background: white; padding: 1rem; border-radius: 8px; }
.error-message { color: var(--semantic-color-text-danger); background-color: var(--semantic-color-surface-danger-secondary); padding: 0.75rem; border-radius: var(--semantic-border-radius-interactive); text-align: center; }
</style>
