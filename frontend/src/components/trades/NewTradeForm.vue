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
      <div class="grid-group grid-group-5-col">
        <BaseInput v-model.number="form.entry_price" label="Entry Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.exit_price" label="Exit Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.position_size" label="Position Size" type="number" step="0.01" />
        <BaseInput v-model.number="form.stop_loss_price" label="Stop Loss" type="number" step="0.01" />
        <BaseInput v-model.number="form.take_profit_price" label="Take Profit" type="number" step="0.01" />
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
/* Diagnostic Styles: Using hardcoded values to bypass CSS variables */
.new-trade-form {
  display: flex;
  flex-direction: column;
  gap: 24px; /* was --semantic-size-stack-lg */
  max-height: 70vh;
  overflow-y: auto;
  padding: 0.5rem;
  margin-right: -1rem;
}

.form-section {
  border: none;
  border-top: 1px solid #E5E7EB; /* was --semantic-color-border-default */
  padding: 32px 0 0 0; /* was --semantic-size-inset-xl */
  margin-top: 24px; /* was --semantic-size-stack-lg */
  display: flex;
  flex-direction: column;
  gap: 16px; /* was --semantic-size-stack-md */
  position: relative;
}

.form-section legend {
  position: absolute;
  top: 0;
  left: 16px;
  transform: translateY(-50%);
  background-color: #FFFFFF; /* was --semantic-color-surface-primary */
  padding: 2px 12px; /* was 2px var(--semantic-size-inset-md) */
  font-weight: 600; /* was --base-font-weight-semibold */
  color: #2563EB; /* was --semantic-color-text-interactive */
  border-radius: 9999px; /* was --base-border-radius-full */
  font-size: 14px; /* was --base-font-size-sm */
  border: 1px solid #E5E7EB; /* was --semantic-color-border-default */
  width: auto;
}

.grid-group {
  display: grid;
  gap: 16px; /* was --semantic-size-stack-md */
  padding: 0 8px; /* was 0 var(--semantic-size-inset-xs) */
}

.grid-group-4-col { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.grid-group-5-col { grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); }
.grid-group-3-col { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
.grid-group-2-col { grid-template-columns: 1fr 1fr; }

.notes-group {
  margin-top: 16px; /* was --semantic-size-stack-sm */
}

.textarea-group {
  display: flex;
  flex-direction: column;
  gap: 4px; /* was --semantic-size-stack-xxs */
}

.textarea-group label {
  font-size: 12px; /* was font-style-label-sm */
  font-weight: 500;
  color: #4B5563; /* was --semantic-color-text-secondary */
  margin-left: 2px;
}

textarea {
  width: 100%;
  padding: 8px; /* was --semantic-size-inset-sm */
  border-radius: 6px; /* was --semantic-border-radius-interactive */
  border: 1px solid #D1D5DB; /* was --semantic-color-border-default */
  background-color: #FFFFFF; /* was --semantic-color-surface-primary */
  color: #111827; /* was --semantic-color-text-primary */
  font-family: inherit;
  font-size: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

textarea:focus {
  outline: none;
  border-color: #3B82F6; /* was --semantic-color-border-focus */
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4); /* was --semantic-effect-shadow-focus-ring */
}

.form-actions {
  margin-top: 16px; /* was --semantic-size-stack-sm */
  display: flex;
  justify-content: flex-end;
  padding-right: 1rem;
}
</style>
