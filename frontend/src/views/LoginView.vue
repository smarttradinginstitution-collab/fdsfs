<!--
// =============================================================================
// FILE: src/views/LoginView.vue
// DESCRIZIONE: La pagina di login dell'applicazione.
// Fornisce un'interfaccia per gli utenti per inserire le loro credenziali
// e accedere al sistema. Gestisce anche il flusso di login a due fattori (MFA).
// =============================================================================
-->
<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const mfaCode = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

// La UI mostra il campo MFA se lo store lo richiede
const showMfaField = computed(() => authStore.mfaRequired);

async function handleSubmit() {
  errorMessage.value = '';
  isLoading.value = true;
  try {
    if (showMfaField.value) {
      // Se il campo MFA è visibile, chiama la verifica con MFA
      await authStore.loginWithMfa(email.value, password.value, mfaCode.value);
    } else {
      // Altrimenti, tenta il login normale
      await authStore.login(email.value, password.value);
    }
    // La redirezione avviene all'interno dello store se il login ha successo
  } catch (error) {
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      // Gestisce sia stringhe di errore semplici che oggetti
      errorMessage.value = typeof detail === 'object' ? detail.message : detail;
    } else {
      errorMessage.value = 'An unexpected error occurred.';
    }
    console.error(error);
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <h1 class="login-title">Bentornato</h1>
        <p class="login-subtitle">Accedi al tuo trading journal</p>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="form-fields">
          <!-- I campi email e password sono disabilitati durante la fase MFA -->
          <BaseInput
            v-model="email"
            label="Email"
            type="email"
            placeholder="iltuoindirizzo@email.com"
            :disabled="showMfaField"
            required
          />
          <BaseInput
            v-model="password"
            label="Password"
            type="password"
            placeholder="••••••••"
            :disabled="showMfaField"
            required
          />
          <!-- Campo per il codice MFA, mostrato solo quando necessario -->
          <BaseInput
            v-if="showMfaField"
            v-model="mfaCode"
            label="Codice di Autenticazione (6 cifre)"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            required
            autocomplete="one-time-code"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <BaseButton type="submit" variant="primary" size="medium" :disabled="isLoading">
          {{ isLoading ? 'Accesso in corso...' : (showMfaField ? 'Verifica Codice' : 'Accedi') }}
        </BaseButton>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: var(--semantic-size-stack-xl);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-card);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-sm);
  margin: var(--semantic-size-gutter-screen);
}

.login-header {
  text-align: center;
  margin-bottom: var(--semantic-size-stack-lg);
}

.login-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-xs);
}

.login-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.error-message {
  background-color: var(--semantic-color-surface-negative-subtle);
  color: var(--semantic-color-text-negative);
  border: 1px solid var(--semantic-color-border-negative);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-body-sm);
  text-align: center;
}
</style>
