<script setup>
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';

defineProps({
  modelValue: {
    type: [String, Array, Object, Number],
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Select options',
  },
  mode: {
    type: String,
    default: 'tags',
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  closeOnSelect: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const handleChange = (value) => {
  emit('update:modelValue', value);
};
</script>

<template>
  <Multiselect
    :value="modelValue"
    :options="options"
    :placeholder="placeholder"
    :mode="mode"
    :searchable="searchable"
    :close-on-select="closeOnSelect"
    @change="handleChange"
    class="multiselect-custom"
    label="label"
    value-prop="value"
    :object="true"
  />
</template>

<style>
/*
  CORREZIONE DEFINITIVA:
  Aggiunta di variabili CSS specifiche per lo stile del dropdown e delle opzioni,
  basate sulla documentazione e il file di stile di default della libreria.
*/
.multiselect-custom {
  /* Stili per il contenitore principale */
  --ms-tag-bg: var(--semantic-color-primary-default);
  --ms-tag-color: var(--semantic-color-primary-text);
  --ms-ring-color: var(--semantic-color-primary-focus);
  --ms-border-color: var(--semantic-color-border-default);
  --ms-border-width: 1px;
  --ms-radius: var(--semantic-border-radius-interactive);
  --ms-bg: var(--semantic-color-surface-primary);
  --ms-color: var(--semantic-color-text-primary);

  /* Stili per il menu a tendina (dropdown) */
  --ms-dropdown-bg: var(--semantic-color-surface-secondary);
  --ms-dropdown-border-color: var(--semantic-color-border-default);

  /* Stili per le opzioni (la chiave della soluzione) */
  --ms-option-bg: var(--semantic-color-surface-secondary);
  --ms-option-color: var(--semantic-color-text-primary);

  /* Stili per opzioni evidenziate (con il mouse) */
  --ms-option-bg-pointed: var(--semantic-color-surface-hover);
  --ms-option-color-pointed: var(--semantic-color-text-primary);

  /* Stili per opzioni selezionate */
  --ms-option-bg-selected: var(--semantic-color-primary-default);
  --ms-option-color-selected: var(--semantic-color-primary-text);
}

.multiselect-custom.is-active {
    box-shadow: none;
}
</style>
