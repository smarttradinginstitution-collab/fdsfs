<!--
// =============================================================================
// FILE: components/ui/BaseInput.vue
// DESCRIZIONE: Questo è un componente UI di base per un campo di input testuale.
// Centralizza lo stile e il comportamento per tutti i campi di input,
// garantendo coerenza nell'applicazione.
// =============================================================================
-->

<script setup>
import { ref, computed } from 'vue';
import { v4 as uuidv4 } from 'uuid';

// --- REFS ---
const inputElement = ref(null);
const uniqueId = ref(`input-${uuidv4()}`);

// --- PROPS ---
defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  placeholder: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  inputmode: {
    type: String,
    default: 'text',
  },
   pattern: {
    type: String,
    default: null,
  },
});

// --- EMITS ---
// Definiamo l'evento `update:modelValue` per far funzionare `v-model`.
const emit = defineEmits(['update:modelValue']);

// --- GESTIONE EVENTI ---
// Questa funzione viene chiamata ogni volta che l'utente digita qualcosa
// nel campo di input (grazie a `@input` nel template).
function onInput(event) {
  // Emettiamo l'evento con il nuovo valore del campo.
  // Questo aggiorna la variabile collegata con `v-model` nel componente genitore.
  emit('update:modelValue', event.target.value);
}

// --- EXPOSE ---
// Esponiamo la funzione `focus` per permettere al genitore di focalizzare
// programmaticamente questo campo di input.
defineExpose({
  focus: () => {
    inputElement.value?.focus();
  },
});
</script>

<template>
  <div class="input-wrapper">
    <label v-if="label" :for="uniqueId" class="input-label">{{ label }}</label>
    <input
      :id="uniqueId"
      ref="inputElement"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :inputmode="inputmode"
      :pattern="pattern"
      class="input-field"
      @input="onInput"
    />
  </div>
</template>

<style scoped>
/* Stili specifici per questo componente. */
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;
}

.input-label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

.input-field {
  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-base-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  /* Transizione fluida per il focus. */
  transition: box-shadow var(--base-animation-duration-fast), border-color var(--base-animation-duration-fast);
}

/* Stile per il testo segnaposto. */
.input-field::placeholder {
  color: var(--semantic-color-text-tertiary);
}

/* Stile quando il campo riceve il focus. */
.input-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Stile quando il campo è disabilitato. */
.input-field:disabled {
  background-color: var(--semantic-color-surface-disabled);
  color: var(--semantic-color-text-disabled);
  cursor: not-allowed;
}
</style>
