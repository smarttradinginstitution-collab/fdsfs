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
  Stili per BaseMultiSelect - Soluzione Definitiva
  - Si utilizza una specificità elevata per sovrascrivere il tema di default.
  =============================================================================
*/

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

/* Sovrascrittura delle variabili CSS della libreria con alta specificità */
.base-multiselect .multiselect-custom {
  --ms-bg: var(--semantic-color-surface-primary);
  --ms-color: var(--semantic-color-text-primary);
  --ms-border-color: var(--semantic-color-border-default);
  --ms-border-width: 1px;
  --ms-radius: var(--semantic-border-radius-interactive);
  --ms-font-size: var(--semantic-font-style-body-sm-font-size);
  --ms-line-height: 1.5;
  --ms-placeholder-color: var(--semantic-color-text-tertiary);

  /* Dropdown */
  --ms-dropdown-bg: var(--semantic-color-surface-secondary);
  --ms-dropdown-border-color: var(--semantic-color-border-default);

  /* Opzioni */
  --ms-option-bg-pointed: var(--semantic-color-surface-primary);
  --ms-option-color-pointed: var(--semantic-color-text-primary);
  --ms-option-bg-selected: var(--semantic-color-interactive-primary-default);
  --ms-option-color-selected: var(--semantic-color-text-on-brand);

  /* Tag */
  --ms-tag-bg: var(--semantic-color-interactive-secondary-default);
  --ms-tag-color: var(--semantic-color-text-primary);
  --ms-tag-radius: var(--semantic-border-radius-pill);

  /* Focus Ring */
  --ms-ring-width: 0px;
  --ms-ring-color: transparent;
}

/* Stile per lo stato attivo/focus, per garantire il bordo corretto */
.base-multiselect .multiselect-custom.is-active {
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/*
  Forza lo sfondo degli elementi interni che potrebbero rimanere bianchi.
  L'uso di !important qui è una misura di sicurezza finale.
*/
.base-multiselect .multiselect-custom .multiselect-search,
.base-multiselect .multiselect-custom .multiselect-tags-search,
.base-multiselect .multiselect-custom .multiselect-input {
  background: transparent !important;
  color: var(--semantic-color-text-primary);
}
</style>
