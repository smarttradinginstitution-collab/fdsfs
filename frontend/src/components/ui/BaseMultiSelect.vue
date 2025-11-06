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
  /* questa la usi nel form: <BaseMultiSelect ... label="Tags" /> */
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
  color: var(--semantic-color-text-primary, #fff);
}

/* variabili del tema del multiselect */
.multiselect-custom {
  --ms-tag-bg: var(--semantic-color-interactive-primary-default);
  --ms-tag-color: var(--semantic-color-text-on-brand);
  --ms-ring-color: var(--semantic-color-border-focus);
  --ms-border-color: var(--semantic-color-border-default);
  --ms-border-width: 1px;
  --ms-radius: 0.4rem;
  --ms-bg: var(--semantic-color-surface-primary);
  --ms-color: var(--semantic-color-text-primary);
  --ms-placeholder-color: var(--semantic-color-text-primary);

  /* dropdown */
  --ms-dropdown-bg: var(--semantic-color-surface-secondary);
  --ms-dropdown-border-color: var(--semantic-color-border-default);
  --ms-option-bg-pointed: var(--semantic-color-surface-primary);
  --ms-option-color-pointed: var(--semantic-color-text-primary);
  --ms-option-bg-selected: var(--semantic-color-interactive-primary-default);
  --ms-option-color-selected: var(--semantic-color-text-on-brand);
}

/* il field quando è attivo */
.multiselect-custom.is-active {
  box-shadow: none;
}

/* 👇 qui forziamo il colore del testo delle opzioni
   ora funziona perché append-to-body=false e sono dentro il componente */
.multiselect-custom .multiselect-option {
  color: var(--semantic-color-text-primary);
}

/* per chi usa tema scuro nello sfondo del field */
.multiselect-custom .multiselect-wrapper {
  background: var(--semantic-color-surface-primary);
}

/* placeholder più visibile */
.multiselect-custom .multiselect-single-label,
.multiselect-custom .multiselect-placeholder {
  color: var(--semantic-color-text-primary);
}

/* togliamo il bg bianco dall'input di ricerca e dall'input generale */
.multiselect-custom .multiselect-search,
.multiselect-custom .multiselect-input {
  background-color: transparent;
}
</style>
