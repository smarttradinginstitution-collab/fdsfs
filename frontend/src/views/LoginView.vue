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
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const errorMessage = ref('');

async function handleLogin() {
  errorMessage.value = '';
  try {
    await authStore.login(email.value, password.value);
    // La redirezione avviene all'interno dell'azione `login` dello store
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Si è verificato un errore inatteso.';
    }
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

      <form class="login-form" @submit.prevent="handleLogin">
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
