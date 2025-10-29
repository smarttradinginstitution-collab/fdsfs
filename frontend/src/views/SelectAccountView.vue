<script setup>
import { onMounted, ref, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const router = useRouter();
const tradingAccountsStore = useTradingAccountsStore();

// --- STATE FOR NEW ACCOUNT CREATION ---
const newAccountName = ref('');
const isCreating = ref(false);

// --- STATE FOR ACCOUNT SELECTION ---
const selectedAccountIds = ref([]);
const isSubmitting = ref(false);
const errorMessage = ref('');


// --- LIFECYCLE HOOKS ---

// Fetch accounts when component is mounted
onMounted(() => {
  tradingAccountsStore.fetchTradingAccounts();
});

// Sync local selection state with the store's state once accounts are loaded
watchEffect(() => {
  if (tradingAccountsStore.tradingAccounts.length > 0) {
    selectedAccountIds.value = tradingAccountsStore.tradingAccounts
      .filter(acc => acc.is_selected)
      .map(acc => acc.id);
  }
});


// --- HANDLERS ---

/**
 * Handles the submission of the account selection form.
 */
async function handleSelectionSubmit() {
  if (isSubmitting.value) return;

  isSubmitting.value = true;
  errorMessage.value = '';
  try {
    await tradingAccountsStore.updateAccountSelection(selectedAccountIds.value);
    // After saving, we must re-fetch the accounts to ensure the store and router guards
    // have the absolute latest state before navigating.
    await tradingAccountsStore.fetchTradingAccounts();
    router.push('/');
  } catch (error) {
    errorMessage.value = 'Errore durante l\'aggiornamento della selezione. Riprova.';
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
}

/**
 * Handles the creation of a new trading account.
 */
async function handleCreateAccount() {
  if (!newAccountName.value.trim()) {
    errorMessage.value = 'Il nome dell\'account non può essere vuoto.';
    return;
  }

  errorMessage.value = '';
  isCreating.value = true;
  try {
    const newAccount = await tradingAccountsStore.createTradingAccount({
      label: newAccountName.value,
    });
    // The store now re-fetches and the backend auto-selects the new account.
    // The router guard will redirect to the dashboard automatically.
    if (newAccount) {
      router.push('/');
    }
  } catch (error) {
    errorMessage.value = 'Errore durante la creazione dell\'account. Riprova.';
    console.error(error);
  } finally {
    isCreating.value = false;
  }
}
</script>

<template>
  <div class="select-account-view">
    <div class="container">
      <div class="header">
        <h1>Seleziona Account di Trading</h1>
        <p v-if="tradingAccountsStore.hasTradingAccounts">
          Scegli con quali account operare. Puoi selezionarne più di uno.
        </p>
        <p v-else>Non hai ancora un account di trading. Creane uno per iniziare.</p>
      </div>

      <!-- Loading State -->
      <div v-if="tradingAccountsStore.isLoading && !tradingAccountsStore.hasTradingAccounts" class="loading-state">
        <p>Caricamento...</p>
      </div>

      <!-- Existing Accounts Selection Form -->
      <form v-else-if="tradingAccountsStore.hasTradingAccounts" class="selection-form" @submit.prevent="handleSelectionSubmit">
        <div class="accounts-list">
          <label
            v-for="account in tradingAccountsStore.tradingAccounts"
            :key="account.id"
            class="account-item"
            :class="{ 'is-selected': selectedAccountIds.includes(account.id) }"
          >
            <input
              type="checkbox"
              :value="account.id"
              v-model="selectedAccountIds"
              class="account-checkbox"
            />
            <span class="account-label">{{ account.label || 'Senza nome' }}</span>
            <span class="account-broker">{{ account.broker?.name || 'Nessun broker' }}</span>
          </label>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <BaseButton
          type="submit"
          variant="primary"
          size="medium"
          :is-loading="isSubmitting"
          :disabled="selectedAccountIds.length === 0"
          class="submit-button"
        >
          Continua
        </BaseButton>
      </form>

      <!-- New Account Creation Form -->
      <div v-else class="creation-form-container">
        <h2>Crea il tuo primo Account</h2>
        <form class="creation-form" @submit.prevent="handleCreateAccount">
          <BaseInput
            v-model="newAccountName"
            label="Nome Account"
            placeholder="Es. Conto Primario"
            required
          />
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <BaseButton type="submit" variant="primary" size="medium" :is-loading="isCreating">
            Crea e Continua
          </BaseButton>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* General Layout */
.select-account-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.container {
  width: 100%;
  max-width: 600px;
  padding: var(--semantic-size-stack-xl);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-card);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-sm);
  margin: var(--semantic-size-gutter-screen);
}

/* Header */
.header {
  text-align: center;
  margin-bottom: var(--semantic-size-stack-lg);
}

.header h1 {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-xs);
}

.header p {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
}

/* States */
.loading-state {
  text-align: center;
  padding: var(--semantic-size-stack-xl);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.error-message {
  background-color: var(--semantic-color-surface-negative-subtle);
  color: var(--semantic-color-text-negative);
  border: 1px solid var(--semantic-color-border-negative);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-body-sm);
  text-align: center;
  margin-top: var(--semantic-size-stack-sm);
}


/* Selection Form */
.selection-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.accounts-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.account-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: var(--semantic-size-inline-md);
  padding: var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-subtle);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.account-item:hover {
  background-color: var(--semantic-color-surface-hover);
  border-color: var(--semantic-color-border-hover);
}

.account-item.is-selected {
  background-color: var(--semantic-color-surface-selected-subtle);
  border-color: var(--semantic-color-border-selected);
}

.account-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--semantic-color-border-selected);
}

.account-label {
  font: var(--semantic-font-style-body-lg-bold);
  color: var(--semantic-color-text-primary);
}

.account-broker {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
  justify-self: end;
}

.submit-button {
  width: 100%;
}


/* Creation Form */
.creation-form-container {
  margin-top: var(--semantic-size-stack-lg);
}

.creation-form-container h2 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
  text-align: center;
}

.creation-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
</style>