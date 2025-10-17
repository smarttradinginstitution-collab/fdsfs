<script setup>
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';

const router = useRouter();
const tradingAccountsStore = useTradingAccountsStore();

const newAccountName = ref('');
const errorMessage = ref('');
const localSelectionIds = ref([]);

// All'avvio, popola la selezione locale con quella dello store
onMounted(() => {
  tradingAccountsStore.fetchTradingAccounts().then(() => {
    localSelectionIds.value = [...tradingAccountsStore.selectedTradingAccountIds];
  });
});

const isConfirmDisabled = computed(() => localSelectionIds.value.length === 0);

// Funzione per confermare la selezione multipla
async function handleConfirmSelection() {
  await tradingAccountsStore.updateAccountSelection(localSelectionIds.value);
  router.push('/');
}

// Funzione per creare un nuovo account
async function handleCreateAccount() {
  if (!newAccountName.value.trim()) {
    errorMessage.value = 'Il nome dell\'account non può essere vuoto.';
    return;
  }
  errorMessage.value = '';

  try {
    // TODO: Sostituire i valori hardcoded con un form di creazione completo
    const newAccount = await tradingAccountsStore.createTradingAccount({
      label: newAccountName.value,
      initial_balance: 0,
      currency: 'USD',
      broker_id: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' // ID Broker di default
    });
    if (newAccount) {
      // La logica di selezione è già nello store, quindi basta reindirizzare
      router.push('/');
    }
  } catch (error) {
    errorMessage.value = 'Errore durante la creazione dell\'account. Riprova.';
    console.error(error);
  }
}
</script>

<template>
  <div class="select-account-view">
    <div class="container">
      <div class="header">
        <h1>Seleziona Account di Trading</h1>
        <p v-if="tradingAccountsStore.hasTradingAccounts">Scegli con quali account operare. Puoi selezionarne più di uno.</p>
        <p v-else>Non hai ancora un account di trading. Creane uno per iniziare.</p>
      </div>

      <!-- Sezione di caricamento -->
      <div v-if="tradingAccountsStore.isLoading" class="loading-state">
        <p>Caricamento...</p>
      </div>

      <!-- Elenco degli account esistenti con checkbox -->
      <div v-else-if="tradingAccountsStore.hasTradingAccounts" class="accounts-list">
        <div
          v-for="account in tradingAccountsStore.tradingAccounts"
          :key="account.id"
          class="account-item"
        >
          <BaseCheckbox
            :id="`account-${account.id}`"
            :value="account.id"
            v-model="localSelectionIds"
          >
            <span class="account-label">{{ account.label || 'Senza nome' }}</span>
          </BaseCheckbox>
          <span class="account-broker">{{ account.broker?.name || 'Nessun broker' }}</span>
        </div>
        <BaseButton
          @click="handleConfirmSelection"
          :disabled="isConfirmDisabled"
          variant="primary"
          size="medium"
          class="confirm-button"
        >
          Conferma e Continua
        </BaseButton>
      </div>

      <!-- Form di creazione nuovo account -->
      <div v-else class="creation-form-container">
        <h2>Crea il tuo primo Account</h2>
        <form class="creation-form" @submit.prevent="handleCreateAccount">
          <BaseInput
            v-model="newAccountName"
            label="Nome Account"
            placeholder="Es. Conto Primario"
            required
          />
          <!-- Come richiesto, il broker non viene selezionato qui per ora -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <BaseButton type="submit" variant="primary" size="medium">
            Crea e Continua
          </BaseButton>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

.loading-state {
  text-align: center;
  padding: var(--semantic-size-stack-xl);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.accounts-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-lg);
  background-color: var(--semantic-color-surface-subtle);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  transition: background-color 0.2s, border-color 0.2s;
}

/* Rimuoviamo l'hover effect che suggerisce un click sull'intera riga */
.account-item:hover {
  background-color: var(--semantic-color-surface-subtle);
  border-color: var(--semantic-color-border-default);
}

.account-label {
  font: var(--semantic-font-style-body-lg-bold);
  color: var(--semantic-color-text-primary);
}

.account-broker {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
}

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

.error-message {
  background-color: var(--semantic-color-surface-negative-subtle);
  color: var(--semantic-color-text-negative);
  border: 1px solid var(--semantic-color-border-negative);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-body-sm);
  text-align: center;
}

.confirm-button {
  margin-top: var(--semantic-size-stack-lg);
  width: 100%;
}
</style>