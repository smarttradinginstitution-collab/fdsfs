<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth.js';
import { useRouter } from 'vue-router';
import BaseButton from '../components/ui/BaseButton.vue';

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');

const handleLogin = async () => {
  try {
    await authStore.login({ email: email.value, password: password.value });
    router.push('/');
  } catch (error) {
    console.error('Login failed:', error);
    // You can add user-facing error handling here
  }
};
</script>

<template>
  <div class="login-view">
    <div class="login-box">
      <h1 class="login-title">Login</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <BaseButton type="submit" variant="primary" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? 'Logging in...' : 'Login' }}
        </BaseButton>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: var(--semantic-size-inset-xl);
  background-color: var(--semantic-color-surface-card);
  border-radius: var(--semantic-border-radius-lg);
  border: 1px solid var(--semantic-color-border-subtle);
}

.login-title {
  text-align: center;
  margin-bottom: var(--semantic-size-stack-lg);
  color: var(--semantic-color-text-default);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

label {
  font-weight: var(--font-weight-medium);
  color: var(--semantic-color-text-subtle);
}

input {
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-md);
  border: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-page);
  color: var(--semantic-color-text-default);
  font-size: var(--font-size-2);
}

input:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: 0 0 0 3px var(--semantic-color-shadow-focus);
}
</style>
