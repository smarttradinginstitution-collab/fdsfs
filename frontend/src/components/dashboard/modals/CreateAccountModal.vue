<script setup>
import { ref } from 'vue';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'account-created']);

const tradingAccountsStore = useTradingAccountsStore();
const newAccountName = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

async function handleCreateAccount() {
  if (!newAccountName.value.trim()) {
    errorMessage.value = 'Il nome dell\'account non può essere vuoto.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const newAccount = await tradingAccountsStore.createTradingAccount({
      label: newAccountName.value,
    });
    emit('account-created', newAccount);
    closeModal();
  } catch (error) {
    errorMessage.value = 'Errore durante la creazione. Riprova.';
    console.error(error);
  } finally {
    isLoading.value = false;
  }
}

function closeModal() {
  newAccountName.value = '';
  errorMessage.value = '';
  isLoading.value = false;
  emit('close');
}
</script>

<template>
  <BaseModal :is-open="isOpen" @close="closeModal">
    <template #header>
      <h2 class="modal-title">Crea Nuovo Account di Trading</h2>
    </template>

    <template #body>
      <p class="modal-description">
        Dai un nome al tuo nuovo account per distinguerlo dagli altri.
      </p>
      <form id="create-account-form" @submit.prevent="handleCreateAccount">
        <BaseInput
          v-model="newAccountName"
          label="Nome Account"
          placeholder="Es. Conto Secondario"
          required
        />
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </form>
    </template>

    <template #footer>
      <BaseButton variant="secondary" @click="closeModal">
        Annulla
      </BaseButton>
      <BaseButton
        type="submit"
        form="create-account-form"
        variant="primary"
        :is-loading="isLoading"
      >
        Crea Account
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.modal-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}

.modal-description {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-lg);
}

#create-account-form {
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