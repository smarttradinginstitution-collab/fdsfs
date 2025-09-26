<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import NewTradeForm from '@/components/trades/NewTradeForm.vue';
import { useTradesStore } from '@/stores/trades';
import { useUiStore } from '@/stores/uiStore';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import UploadIcon from '@/components/icons/UploadIcon.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import TradeImporter from '@/components/import/TradeImporter.vue';

const router = useRouter();
const tradesStore = useTradesStore();
const uiStore = useUiStore();
const tradingAccountsStore = useTradingAccountsStore();

const choice = ref(null); // 'manual' or 'import'

// --- Computed Properties ---
const selectedAccountId = computed(() => tradingAccountsStore.selectedTradingAccount?.id);

const accountOptions = computed(() =>
  tradingAccountsStore.tradingAccounts.map(acc => ({
    value: acc.id,
    text: acc.label,
  }))
);

// --- Lifecycle Hooks ---
onMounted(() => {
  // Ensure trading accounts are loaded when the component is mounted
  if (!tradingAccountsStore.hasTradingAccounts) {
    tradingAccountsStore.fetchTradingAccounts();
  }
});

// --- Methods ---
const handleAccountSelection = (accountId) => {
  const selectedAccount = tradingAccountsStore.tradingAccounts.find(
    (acc) => acc.id === accountId
  );
  tradingAccountsStore.selectTradingAccount(selectedAccount);
};

const handleNewTrade = async (tradeData) => {
  try {
    const newTrade = await tradesStore.addTrade(tradeData);
    if (newTrade) {
      uiStore.showNotification({
        message: 'Trade successfully created!',
        type: 'success',
      });
      router.push('/trades');
    }
  } catch (error) {
    console.error('Failed to add trade:', error);
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  }
};
</script>

<template>
  <div class="add-trade-container">
    <div v-if="!choice" class="selection-view">
      <div class="header">
        <h1 class="title">Add a New Trade</h1>
        <p class="subtitle">How would you like to add your trade?</p>
      </div>

      <div class="card-deck">
        <!-- Manual Entry Card -->
        <div class="card" @click="choice = 'manual'">
          <div class="card-icon-wrapper">
            <PlusIcon class="card-icon" />
          </div>
          <div class="card-content">
            <h3 class="card-title">Manual Entry</h3>
            <p class="card-description">Add a single trade by filling out a form.</p>
          </div>
          <span class="card-chevron">&gt;</span>
        </div>

        <!-- Import from Broker Card -->
        <div class="card" @click="choice = 'import'">
          <div class="card-icon-wrapper">
            <UploadIcon class="card-icon" />
          </div>
          <div class="card-content">
            <h3 class="card-title">Import from Broker</h3>
            <p class="card-description">Upload a file from your brokerage account.</p>
          </div>
          <span class="card-chevron">&gt;</span>
        </div>
      </div>
    </div>

    <div v-else-if="choice === 'manual'" class="form-view">
      <div class="form-header">
        <BaseButton @click="choice = null" variant="secondary" class="back-button">
            &larr; Back to selection
        </BaseButton>
        <h1 class="title">Manual Trade Entry</h1>
      </div>
      <NewTradeForm @submit="handleNewTrade" />
    </div>

    <div v-else-if="choice === 'import'" class="form-view">
      <div class="form-header">
        <BaseButton @click="choice = null" variant="secondary" class="back-button">
            &larr; Back to selection
        </BaseButton>
        <h1 class="title">Import from Broker</h1>
      </div>

      <!-- Step 1: Select Trading Account -->
      <div class="import-step">
        <h2 class="step-title">Step 1: Select a Trading Account</h2>
        <p class="step-description">Choose the account you want to import trades into.</p>
        <BaseSelect
          label="Trading Account"
          :model-value="selectedAccountId"
          :options="accountOptions"
          @update:modelValue="handleAccountSelection"
        />
      </div>

      <!-- Step 2: Upload File (shown only after account selection) -->
      <div v-if="selectedAccountId" class="import-step">
        <h2 class="step-title">Step 2: Upload Your File</h2>
        <p class="step-description">Select the 'Performance' CSV file exported from your broker.</p>
        <TradeImporter />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/mixins';

.add-trade-container {
  padding: var(--semantic-size-inset-xl);
  width: 100%;
  display: flex;
  justify-content: center;
}

.selection-view,
.form-view {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xl);
}

.header {
  text-align: center;
}

.title {
  font: var(--semantic-font-style-heading-h2);
  color: var(--semantic-color-text-primary);
}

.subtitle {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xs);
}

.card-deck {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--semantic-size-stack-lg);
}

@include media-up('md') {
  .card-deck {
    grid-template-columns: 1fr 1fr;
  }
}

.card {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-lg);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  position: relative;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--semantic-effect-shadow-md);
  border-color: var(--semantic-color-border-accent);
}

.card.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.card.disabled:hover {
    transform: none;
    box-shadow: none;
    border-color: var(--semantic-color-border-default);
}

.card-icon-wrapper {
  flex-shrink: 0;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--base-border-radius-full);
  padding: var(--semantic-size-inset-md);
  display: grid;
  place-items: center;
}

.card-icon {
  width: 28px;
  height: 28px;
  color: var(--semantic-color-text-accent);
}

.card-content {
  flex-grow: 1;
}

.card-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
}

.card-description {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xs);
}

.card-chevron {
  font-size: 24px;
  color: var(--semantic-color-text-disabled);
  transition: transform 0.2s ease-in-out;
}

.card:hover .card-chevron {
  transform: translateX(4px);
}

.card-badge {
    position: absolute;
    top: -12px;
    right: 16px;
    background-color: var(--semantic-color-surface-accent);
    color: var(--semantic-color-text-on-brand);
    padding: 4px 10px;
    border-radius: var(--semantic-border-radius-pill);
    font: var(--semantic-font-style-label-sm);
    font-weight: 600;
}

.form-header {
    display: flex;
    align-items: center;
    // justify-content: space-between;
    gap: var(--semantic-size-stack-lg);
    margin-bottom: var(--semantic-size-stack-lg);
    padding-bottom: var(--semantic-size-stack-lg);
    border-bottom: 1px solid var(--semantic-color-border-default);
}

.back-button {
    flex-shrink: 0;
}

.form-header .title {
    flex-grow: 1;
}

.import-step {
    background-color: var(--semantic-color-surface-secondary);
    padding: var(--semantic-size-inset-lg);
    border-radius: var(--semantic-border-radius-surface);
    border: 1px solid var(--semantic-color-border-subtle);
}

.step-title {
    font: var(--semantic-font-style-heading-h5);
    color: var(--semantic-color-text-primary);
}

.step-description {
    font: var(--semantic-font-style-body-sm);
    color: var(--semantic-color-text-secondary);
    margin-top: var(--semantic-size-stack-xs);
    margin-bottom: var(--semantic-size-stack-lg);
}
</style>