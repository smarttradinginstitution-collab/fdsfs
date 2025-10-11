<!--
// =============================================================================
// FILE: src/views/RegisterView.vue
// DESCRIZIONE: Pagina di registrazione per nuovi utenti.
// =============================================================================
-->
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const authStore = useAuthStore();
const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref('');

async function handleRegister() {
  errorMessage.value = '';

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Le password non corrispondono.';
    return;
  }

  try {
    await authStore.register(name.value, email.value, password.value);
    // In caso di successo, il redirect con messaggio verrà gestito nello store
    // o qui, a seconda dell'implementazione finale. Per ora, reindirizziamo.
    router.push({ name: 'login', query: { registered: 'true' } });
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Errore durante la registrazione. Riprova.';
    console.error('Registration error:', error);
  }
}
</script>

<template>
  <div class="register-view">
    <div class="register-container">
      <div class="register-header">
        <h1 class="register-title">Crea il tuo Account</h1>
        <p class="register-subtitle">Inizia a tracciare il tuo percorso di trading</p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-fields">
          <BaseInput
            v-model="name"
            label="Nome"
            type="text"
            placeholder="Mario Rossi"
            required
          />
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
          <BaseInput
            v-model="confirmPassword"
            label="Conferma Password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        <BaseButton type="submit" variant="primary" size="medium">
          Registrati
        </BaseButton>
      </form>

      <div class="login-link">
        <span>Hai già un account? </span>
        <router-link to="/login">Accedi</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: var(--semantic-size-stack-xl);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-card);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-sm);
  margin: var(--semantic-size-gutter-screen);
}

.register-header {
  text-align: center;
  margin-bottom: var(--semantic-size-stack-lg);
}

.register-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-xs);
}

.register-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
}

.register-form {
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

.login-link {
  margin-top: var(--semantic-size-stack-lg);
  text-align: center;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.login-link a {
  color: var(--semantic-color-text-action-primary);
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>