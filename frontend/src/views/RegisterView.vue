<script setup>
import { ref } from 'vue';
import { supabase } from '@/services/supabase';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import { RouterLink } from 'vue-router';

const name = ref('');
const email = ref('');
const password = ref('');
const passwordConfirm = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const loading = ref(false);

async function handleRegister() {
  if (password.value !== passwordConfirm.value) {
    errorMessage.value = 'Le password non coincidono.';
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    const { error } = await supabase.auth.signUp({
      email: email.value,
      password: password.value,
      options: {
        data: {
          full_name: name.value,
        },
      },
    });

    if (error) {
      throw error;
    }

    successMessage.value = 'Registrazione avvenuta con successo! Controlla la tua email per confermare il tuo account.';

  } catch (error) {
    errorMessage.value = error.message || 'Si è verificato un errore durante la registrazione.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="register-view">
    <div class="register-container">
      <div class="register-header">
        <h1 class="register-title">Crea un account</h1>
        <p class="register-subtitle">Inizia il tuo viaggio nel trading journal</p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div v-if="!successMessage" class="form-fields">
          <BaseInput
            v-model="name"
            label="Nome"
            type="text"
            placeholder="Il tuo nome"
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
            v-model="passwordConfirm"
            label="Conferma Password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <BaseButton v-if="!successMessage" type="submit" variant="primary" size="medium" :disabled="loading">
          {{ loading ? 'Creazione...' : 'Crea Account' }}
        </BaseButton>

        <div class="login-link">
          Hai già un account?
          <RouterLink to="/login">Accedi</RouterLink>
        </div>
      </form>
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

.success-message {
  background-color: var(--semantic-color-surface-positive-subtle);
  color: var(--semantic-color-text-positive);
  border: 1px solid var(--semantic-color-border-positive);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-body-sm);
  text-align: center;
}

.login-link {
  text-align: center;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.login-link a {
  color: var(--semantic-color-text-action-primary-default);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>