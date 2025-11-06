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
/*
  =============================================================================
  Stili per BaseMultiSelect
  - Sovrascrive la libreria @vueform/multiselect per il tema scuro
  - Allinea le label allo stile di BaseSelect
  =============================================================================
*/

/* Wrapper del campo per allinearlo agli altri input */
.base-multiselect {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: var(--semantic-size-stack-xs);
}

.base-multiselect__label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

/* Variabili globali per sovrascrivere il tema di default */
.multiselect-custom {
  --ms-font-size: var(--semantic-font-style-body-sm-font-size);
  --ms-radius: var(--semantic-border-radius-interactive);

  /* Sfondo e testo */
  --ms-bg: var(--semantic-color-surface-primary) !important;
  --ms-color: var(--semantic-color-text-primary) !important;
  --ms-placeholder-color: var(--semantic-color-text-tertiary) !important;

  /* Bordi e focus */
  --ms-border-width: 1px;
  --ms-border-color: var(--semantic-color-border-default);
  --ms-ring-width: 0px;
  --ms-ring-color: transparent;
  box-shadow: none;

  /* Dropdown */
  --ms-dropdown-bg: var(--semantic-color-surface-secondary) !important;
  --ms-dropdown-border-color: var(--semantic-color-border-default) !important;

  /* Opzioni */
  --ms-option-bg-pointed: var(--semantic-color-surface-primary) !important;
  --ms-option-color-pointed: var(--semantic-color-text-primary) !important;
  --ms-option-bg-selected: var(--semantic-color-interactive-primary-default) !important;
  --ms-option-color-selected: var(--semantic-color-text-on-brand) !important;

  /* Tag (pills) */
  --ms-tag-bg: var(--semantic-color-interactive-secondary-default) !important;
  --ms-tag-color: var(--semantic-color-text-primary) !important;
  --ms-tag-radius: var(--semantic-border-radius-pill) !important;
}

/* Forza lo sfondo del campo di ricerca interno */
.multiselect-custom .multiselect-search {
  background-color: transparent !important;
}

/* Stile aggiuntivo per lo stato :active (focus) */
.multiselect-custom.is-active {
  border-color: var(--semantic-color-border-focus) !important;
  box-shadow: var(--semantic-effect-shadow-focus-ring) !important;
}
</style>
