<!--
// =============================================================================
// FILE: src/views/LoginView.vue
// DESCRIZIONE: La pagina di login dell'applicazione.
// Fornisce un'interfaccia per gli utenti per inserire le loro credenziali
// e accedere al sistema.
// =============================================================================
-->
<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/uiStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const authStore = useAuthStore();
const uiStore = useUiStore();
const email = ref('');
const password = ref('');
const otpCode = ref('');
const errorMessage = ref('');
const isMfaStep = ref(false); // Nuovo stato per gestire il flusso MFA

async function handleLogin() {
  errorMessage.value = '';
  try {
    const result = await authStore.login(email.value, password.value);
    if (result.mfaRequired) {
      isMfaStep.value = true; // Mostra il form per l'OTP
    }
    // Se non è richiesta MFA, la redirezione avviene nello store
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Credenziali non valide o errore inatteso.';
    console.error(error);
  }
}

async function handleMfaVerification() {
  errorMessage.value = '';
  try {
    await authStore.verifyMfaAndLogin(otpCode.value);
    // La redirezione avviene nello store dopo la verifica
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Codice OTP non valido o errore inatteso.';
    console.error(error);
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

      <!-- Form di Login Standard -->
      <form v-if="!isMfaStep" class="login-form" @submit.prevent="handleLogin">
        <div class="form-fields">
          <BaseInput
            v-model="email"
            label="Email"
            type="email"
            placeholder="iltuoindirizzo@email.com"
            required
          />
          <BaseInput
            v-model="password"
            label="Password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        <BaseButton type="submit" variant="primary" size="medium">
          Accedi
        </BaseButton>
      </form>

      <!-- Form per Inserimento Codice MFA/OTP -->
      <form v-else class="login-form" @submit.prevent="handleMfaVerification">
        <div class="form-fields">
          <p class="login-subtitle">Controlla la tua app di autenticazione e inserisci il codice.</p>
          <BaseInput
            v-model="otpCode"
            label="Codice di Verifica"
            type="text"
            placeholder="123456"
            required
            inputmode="numeric"
            pattern="\d{6}"
          />
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        <BaseButton type="submit" variant="primary" size="medium">
          Verifica Codice
        </BaseButton>
      </form>

      <div class="signup-link">
        <p>
          Non hai un account?
          <router-link :to="{ name: 'signup' }">Registrati</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.signup-link {
  margin-top: var(--semantic-size-stack-lg);
  text-align: center;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.signup-link a {
  color: var(--semantic-color-text-interactive);
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}

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
