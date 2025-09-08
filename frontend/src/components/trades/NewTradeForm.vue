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
  lowest_price_during_trade: null,
  highest_price_during_trade: null,
  entry_timestamp: null,
  exit_timestamp: null,
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

    <fieldset class="form-section">
      <legend>Core Information</legend>
      <div class="grid-group grid-group-4-col">
        <BaseInput v-model="form.ticker" label="Ticker" placeholder="e.g., AAPL" />
        <BaseSelect v-model="form.direction" label="Direction" :options="[{value: 'Long', text: 'Long'}, {value: 'Short', text: 'Short'}]" />
        <BaseInput v-model.number="form.pnl" label="Net P&L" type="number" step="0.01" />
        <BaseInput v-model="form.setup" label="Setup / Strategy" placeholder="e.g., Breakout" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Prices & Size</legend>
      <div class="grid-group grid-group-4-col">
        <BaseInput v-model.number="form.entry_price" label="Entry Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.exit_price" label="Exit Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.stop_loss_price" label="Stop Loss" type="number" step="0.01" />
        <BaseInput v-model.number="form.take_profit_price" label="Take Profit" type="number" step="0.01" />
        <BaseInput v-model.number="form.lowest_price_during_trade" label="Lowest Price (MAE)" type="number" step="0.01" />
        <BaseInput v-model.number="form.highest_price_during_trade" label="Highest Price (MFE)" type="number" step="0.01" />
        <BaseInput v-model.number="form.position_size" label="Position Size" type="number" step="0.01" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Timestamps</legend>
      <div class="grid-group grid-group-2-col">
        <BaseInput v-model="form.entry_timestamp" label="Entry Timestamp" type="datetime-local" />
        <BaseInput v-model="form.exit_timestamp" label="Exit Timestamp" type="datetime-local" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Analysis & Review</legend>
      <div class="grid-group grid-group-3-col">
        <BaseInput v-model="form.emotional_state" label="Emotional State" placeholder="e.g., Confident" />
        <BaseInput v-model="form.mistakes" label="Mistakes" placeholder="e.g., FOMO, over-leveraged" />
        <BaseInput v-model="form.tags" label="Tags" placeholder="e.g., news, earnings" />
      </div>
      <div class="grid-group grid-group-2-col notes-group">
        <div class="textarea-group">
          <label>Pre-Trade Notes</label>
          <textarea v-model="form.notes_pre_trade" rows="4"></textarea>
        </div>
        <div class="textarea-group">
          <label>Post-Trade Notes</label>
          <textarea v-model="form.notes_post_trade" rows="4"></textarea>
        </div>
      </div>
       <div class="textarea-group">
        <label>General Notes</label>
        <textarea v-model="form.notes" rows="4"></textarea>
      </div>
    </fieldset>

    <div class="form-actions">
      <BaseButton type="submit">Save Trade</BaseButton>
    </div>
  </form>
</template>

<style scoped>
/* Using hardcoded values for diagnosis to bypass any CSS token/variable issues */
.new-trade-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 70vh;
  overflow-y: auto;
  padding: 8px;
  margin-right: -12px;
}

.form-section {
  border: none;
  border-top: 1px solid #E5E7EB; /* light gray */
  padding: 24px 0 0 0;
  margin-top: 24px;
  position: relative;
}

.form-section:first-of-type {
  margin-top: 0;
}

.form-section legend {
  position: absolute;
  top: 0;
  left: 16px;
  transform: translateY(-50%);
  background: #FFFFFF; /* Match modal background */
  padding: 2px 12px;
  font-weight: 600;
  color: #1E40AF; /* A deep blue for professionalism */
  font-size: 14px;
  width: auto;
}

.grid-group {
  display: grid;
  gap: 16px;
  padding: 0 8px;
}

.grid-group-4-col { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.grid-group-3-col { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
.grid-group-2-col { grid-template-columns: 1fr 1fr; }

.notes-group {
  margin-top: 8px;
}

.textarea-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.textarea-group label {
  font-size: 12px;
  font-weight: 500;
  color: #4B5563; /* Gray */
  margin-left: 2px;
}

textarea {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #D1D5DB; /* Gray */
  background-color: #FFFFFF;
  color: #111827; /* Black */
  font-family: inherit;
  font-size: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

textarea:focus {
  outline: none;
  border-color: #3B82F6; /* Blue */
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
}

.form-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  padding-right: 1rem;
}
</style>
