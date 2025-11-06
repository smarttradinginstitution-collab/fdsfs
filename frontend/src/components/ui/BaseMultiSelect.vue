<!-- frontend/src/components/ui/BaseMultiSelect.vue -->
<script setup>
import Multiselect from '@vueform/multiselect'
import '@vueform/multiselect/themes/default.css'

const props = defineProps({
  modelValue: {
    type: [String, Array, Object, Number, null],
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
    default: 'tags', // single | multiple | tags
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  closeOnSelect: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const handleChange = (value) => {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="base-multiselect">
    <label v-if="label" class="base-multiselect__label">
      {{ label }}
    </label>

    <Multiselect :value="modelValue" :options="options" :placeholder="placeholder" :mode="mode" :searchable="searchable"
      :close-on-select="closeOnSelect" :append-to-body="false" @change="handleChange" class="multiselect-custom"
      label="label" value-prop="value" :object="false" />
  </div>
</template>

<style>
/* wrapper del campo per allinearlo agli altri input */
.base-multiselect {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.base-multiselect__label {
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--semantic-color-text-primary);
}

/*
  Soluzione Definitiva per il Tema Scuro del Multiselect

  1. Variabili Globali: Sovrascriviamo le variabili CSS di default della libreria
     per allinearle al nostro design system.
  2. Regole Specifiche: Applichiamo regole dirette ai selettori interni
     (es. `.multiselect-search`) per forzare lo stile corretto, superando
     le regole di default del file `default.css` importato.
*/

/* 1. Variabili Globali */
.multiselect-custom {
  --ms-radius: var(--semantic-border-radius-interactive);
  --ms-bg: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  --ms-ring-color: var(--semantic-color-border-focus);
  --ms-placeholder-color: var(--semantic-color-text-primary);
  --ms-color: var(--semantic-color-text-primary);

  --ms-tag-bg: var(--semantic-color-interactive-primary-default);
  --ms-tag-color: var(--semantic-color-text-on-brand);

  --ms-dropdown-bg: var(--semantic-color-surface-secondary);
  --ms-dropdown-border-color: var(--semantic-color-border-default);

  --ms-option-bg-pointed: var(--semantic-color-surface-primary);
  --ms-option-color-pointed: var(--semantic-color-text-primary);
  --ms-option-bg-selected: var(--semantic-color-interactive-primary-default);
  --ms-option-color-selected: var(--semantic-color-text-on-brand);
}

/* 2. Regole Specifiche */

/* Sfondo per il campo di input (sia vuoto che in modalità tags) */
.multiselect-custom .multiselect-search,
.multiselect-custom .multiselect-tags-search,
.multiselect-custom .multiselect-input {
  background: transparent;
  color: var(--semantic-color-text-primary);
}

/* Colore del placeholder */
.multiselect-custom .multiselect-placeholder {
  color: var(--semantic-color-text-primary);
}

/* Wrapper principale per garantire lo sfondo corretto */
.multiselect-custom .multiselect-wrapper {
  background: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-interactive);
}

/* Testo delle opzioni nel dropdown */
.multiselect-custom .multiselect-option {
  color: var(--semantic-color-text-primary);
}

/* Stile del bordo quando il componente è attivo/focalizzato */
.multiselect-custom.is-active {
  box-shadow: none;
  border-color: var(--semantic-color-border-focus);
}
</style>
