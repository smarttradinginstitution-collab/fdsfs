<!--
// =============================================================================
// FILE: components/trades/NewTradeForm.vue
// DESCRIZIONE: Questo è un componente specifico che rappresenta il form
// per inserire un nuovo trade. Viene tipicamente usato all'interno di una
// finestra modale.
// =============================================================================
-->

<script setup>
import { ref } from 'vue';
import BaseInput from '../ui/BaseInput.vue';
import BaseButton from '../ui/BaseButton.vue';
import BaseSelect from '../ui/BaseSelect.vue';

const emit = defineEmits(['submit']);

const getInitialFormState = () => ({
  ticker: '',
  pnl: 0,
  setup: '',
  direction: null,
  entry_price: null,
  exit_price: null,
  stop_loss_price: null,
  take_profit_price: null,
  position_size: null,
  notes: '',
  notes_pre_trade: '',
  notes_post_trade: '',
  emotional_state: '',
  mistakes: '', // Verrà inviato come stringa, il backend si aspetta una lista
  tags: '',       // Verrà inviato come stringa, il backend si aspetta una lista
});

const form = ref(getInitialFormState());

const handleSubmit = () => {
  const tradeData = { ...form.value };

  // Converte le stringhe di 'mistakes' e 'tags' in array
  if (tradeData.mistakes) {
    tradeData.mistakes = tradeData.mistakes.split(',').map(s => s.trim()).filter(Boolean);
  } else {
    tradeData.mistakes = [];
  }

  if (tradeData.tags) {
    tradeData.tags = tradeData.tags.split(',').map(s => s.trim()).filter(Boolean);
  } else {
    tradeData.tags = [];
  }

  emit('submit', tradeData);
  form.value = getInitialFormState();
};
</script>

<template>
  <form class="new-trade-form" @submit.prevent="handleSubmit">
    <div class="form-grid">
      <!-- Core Info -->
      <BaseInput v-model="form.ticker" label="Ticker" placeholder="e.g., AAPL" />
      <BaseSelect v-model="form.direction" label="Direction" :options="[{value: 'Long', text: 'Long'}, {value: 'Short', text: 'Short'}]" />
      <BaseInput v-model.number="form.pnl" label="Net P&L" type="number" step="0.01" />
      <BaseInput v-model="form.setup" label="Setup / Strategy" placeholder="e.g., Breakout" />

      <!-- Prices -->
      <BaseInput v-model.number="form.entry_price" label="Entry Price" type="number" step="0.01" />
      <BaseInput v-model.number="form.exit_price" label="Exit Price" type="number" step="0.01" />
      <BaseInput v-model.number="form.stop_loss_price" label="Stop Loss" type="number" step="0.01" />
      <BaseInput v-model.number="form.take_profit_price" label="Take Profit" type="number" step="0.01" />

      <!-- Details -->
      <BaseInput v-model.number="form.position_size" label="Position Size" type="number" step="0.01" />
      <BaseInput v-model="form.emotional_state" label="Emotional State" placeholder="e.g., Confident" />
      <BaseInput v-model="form.mistakes" label="Mistakes" placeholder="e.g., FOMO, over-leveraged" />
      <BaseInput v-model="form.tags" label="Tags" placeholder="e.g., news, earnings" />
    </div>

    <!-- Notes -->
    <div class="notes-grid">
      <div class="textarea-group">
        <label>Pre-Trade Notes</label>
        <textarea v-model="form.notes_pre_trade" rows="3"></textarea>
      </div>
      <div class="textarea-group">
        <label>Post-Trade Notes</label>
        <textarea v-model="form.notes_post_trade" rows="3"></textarea>
      </div>
      <div class="textarea-group full-width">
        <label>General Notes</label>
        <textarea v-model="form.notes" rows="4"></textarea>
      </div>
    </div>

    <div class="form-actions">
      <BaseButton type="submit">Save Trade</BaseButton>
    </div>
  </form>
</template>

<style scoped>
.new-trade-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 1rem; /* Per dare spazio alla scrollbar */
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.notes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--semantic-size-stack-md);
}

.textarea-group {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.textarea-group.full-width {
  grid-column: 1 / -1;
}

.textarea-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-subtle);
}

textarea {
  width: 100%;
  padding: var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-md);
  border: 1px solid var(--color-border-subtle);
  background-color: var(--color-background-subtle);
  color: var(--color-text-default);
  font-family: inherit;
  font-size: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

textarea:focus {
  outline: none;
  border-color: var(--color-border-accent);
  box-shadow: 0 0 0 2px var(--color-focus-ring);
}

.form-actions {
  margin-top: var(--semantic-size-stack-md);
  display: flex;
  justify-content: flex-end; /* Allinea il bottone a destra. */
}
</style>
