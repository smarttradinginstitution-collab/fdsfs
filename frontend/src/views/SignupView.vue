<!--
// =============================================================================
// FILE: src/views/SignupView.vue
// DESCRIZIONE: Pagina di registrazione per i nuovi utenti.
// =============================================================================
-->
<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const authStore = useAuthStore();

const firstName = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref(null);
const validationErrors = ref({});
const isRegistered = ref(false); // Stato per mostrare il messaggio di successo

const passwordError = computed(() => {
  if (password.value && confirmPassword.value && password.value !== confirmPassword.value) {
    return 'Le password non coincidono.';
  }
  return '';
});

async function handleSignup() {
  error.value = null;
  validationErrors.value = {};

  if (password.value !== confirmPassword.value) {
    validationErrors.value.confirmPassword = 'Le password non coincidono.';
    return;
  }

  try {
    await authStore.register(firstName.value, email.value, password.value);
    isRegistered.value = true; // Mostra il messaggio di successo
  } catch (err) {
    error.value = err.response?.data?.detail || 'Si è verificato un errore durante la registrazione.';
  }
}
</script>

<template>
  <div class="signup-view">
    <div class="signup-container">
      <!-- Sezione di Successo -->
      <div v-if="isRegistered" class="registration-success">
        <h1 class="signup-title">Registrazione quasi completata!</h1>
        <p class="signup-subtitle">
          Controlla la tua email per il link di conferma.
        </p>
        <router-link :to="{ name: 'login' }" class="back-to-login-link">
          Torna al Login
        </router-link>
      </div>

      <!-- Form di Registrazione -->
      <div v-else>
        <div class="signup-header">
          <h1 class="signup-title">Crea il tuo account</h1>
          <p class="signup-subtitle">Inizia a tracciare i tuoi progressi di trading.</p>
        </div>

        <form class="signup-form" @submit.prevent="handleSignup">
          <div class="form-fields">
            <BaseInput
              v-model="firstName"
              label="Nome"
              type="text"
              placeholder="Mario"
              required
              :error="validationErrors.firstName"
            />
            <BaseInput
              v-model="email"
              label="Email"
              type="email"
              placeholder="iltuoindirizzo@email.com"
              required
              :error="validationErrors.email"
            />
            <BaseInput
              v-model="password"
              label="Password"
              type="password"
              placeholder="••••••••"
              required
              :error="validationErrors.password"
            />
            <BaseInput
              v-model="confirmPassword"
              label="Conferma Password"
              type="password"
              placeholder="••••••••"
              required
              :error="passwordError || validationErrors.confirmPassword"
            />
          </div>
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          <BaseButton type="submit" variant="primary" size="medium">
            Registrati
          </BaseButton>
        </form>

        <div class="login-link">
          <p>
            Hai già un account?
            <router-link :to="{ name: 'login' }">Accedi</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.registration-success {
  text-align: center;
  padding: var(--semantic-size-stack-xl) 0;
}

.back-to-login-link {
  display: inline-block;
  margin-top: var(--semantic-size-stack-lg);
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-interactive);
  text-decoration: none;
  font-weight: 500;
}

.back-to-login-link:hover {
  text-decoration: underline;
}

.signup-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.signup-container {
  width: 100%;
  max-width: 400px;
  padding: var(--semantic-size-stack-xl);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-card);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-sm);
  margin: var(--semantic-size-gutter-screen);
}

.signup-header {
  text-align: center;
  margin-bottom: var(--semantic-size-stack-lg);
}

.signup-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-xs);
}

.signup-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
}

.signup-form {
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
  color: var(--semantic-color-text-interactive);
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>