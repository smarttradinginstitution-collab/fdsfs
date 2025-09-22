<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import BaseButton from '@/components/ui/BaseButton.vue';
import NewTradeForm from '@/components/trades/NewTradeForm.vue';
import { useTradesStore } from '@/stores/trades';
import { useUiStore } from '@/stores/uiStore';

const router = useRouter();
const tradesStore = useTradesStore();
const uiStore = useUiStore();

const choice = ref(null); // can be 'manual' or 'import'

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
  <div class="add-trade-view">
    <h1 class="view-title">How do you want to add your trade?</h1>

    <!-- Step 1: Choice -->
    <div v-if="!choice" class="options-container">
      <BaseButton
        @click="choice = 'manual'"
        class="base-button"
      >
        Manual
      </BaseButton>
      <BaseButton
        @click="choice = 'import'"
        class="base-button"
        disabled
      >
        Import from Broker
      </BaseButton>
    </div>

    <!-- Step 2: Form or Import UI -->
    <div v-if="choice === 'manual'" class="form-container">
       <BaseButton @click="choice = null" variant="secondary" class="back-button">
        &larr; Go Back
      </BaseButton>
      <NewTradeForm @submit="handleNewTrade" />
    </div>

    <div v-if="choice === 'import'" class="import-container">
       <BaseButton @click="choice = null" variant="secondary" class="back-button">
        &larr; Go Back
      </BaseButton>
      <p>Import functionality is coming soon!</p>
    </div>

  </div>
</template>

<style scoped>
.add-trade-view {
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  align-items: center; /* Center children horizontally */
  gap: var(--semantic-size-stack-xl);
  width: 100%;
}

.view-title {
  font: var(--semantic-font-style-heading-h2);
  color: var(--semantic-color-text-primary);
  text-align: center;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  width: 100%;
  max-width: 400px;
}

.base-button {
  padding: var(--semantic-size-inset-xl);
  font: var(--semantic-font-style-heading-h4);
  transition: all 0.2s ease-in-out;
}

.base-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--semantic-effect-shadow-lg);
}

.form-container,
.import-container {
  margin-top: var(--semantic-size-stack-lg);
  width: 100%;
  max-width: 900px; /* Adjust as needed */
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-xl);
  border-radius: var(--semantic-border-radius-container);
  box-shadow: var(--semantic-effect-shadow-md);
  position: relative;
}

.import-container {
  display: grid;
  place-items: center;
  min-height: 200px;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-lg);
}

.back-button {
  position: absolute;
  top: var(--semantic-size-inset-md);
  left: var(--semantic-size-inset-md);
}
</style>
