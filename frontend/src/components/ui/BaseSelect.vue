<!--
=============================================================================
FILE: components/ui/BaseSelect.vue
DESCRIZIONE: Select base con supporto a option.label e option.text
=============================================================================
-->

<script setup>
// --- PROPS ---
const props = defineProps({
  modelValue: {
    type: [String, Number, Array, null],
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  options: {
    type: Array,
    required: true,
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  /**
   * se vuoi una voce vuota in cima (per i playbook)
   */
  placeholder: {
    type: String,
    default: '',
  },
})

// --- EMITS ---
const emit = defineEmits(['update:modelValue'])

// --- GESTIONE EVENTI ---
function onChange(event) {
  if (props.multiple) {
    const selectedValues = Array.from(event.target.selectedOptions).map(
      (option) => option.value,
    )
    emit('update:modelValue', selectedValues)
  } else {
    const value = event.target.value
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="select-wrapper">
    <label v-if="label" class="select-label">{{ label }}</label>
    <div class="select-container">
      <select class="select-field" :value="modelValue" :multiple="multiple" @change="onChange">
        <!-- option vuota, utile per i playbook -->
        <option v-if="!multiple && placeholder" value="" disabled>
          {{ placeholder }}
        </option>

        <option v-for="option in options" :key="option.value" :value="option.value">
          <!-- supporta sia {label:} che {text:} -->
          {{ option.label ?? option.text ?? option.value }}
        </option>
      </select>
    </div>
  </div>
</template>

<style scoped>
/* Stili principali del wrapper e della label */
.select-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;
}

.select-label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

.select-container {
  position: relative;
}

/* Stile del campo select principale */
.select-field {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  cursor: pointer;

  /* Utilizzo dei token semantici per garantire coerenza */
  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-sm-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  padding-right: var(--semantic-size-inset-xl);
  line-height: 1.2;

  transition: box-shadow var(--base-animation-duration-fast),
    border-color var(--base-animation-duration-fast);
}

/* Placeholder style */
.select-field:invalid,
.select-field option[value=""] {
  color: var(--semantic-color-text-tertiary);
}

.select-field option:not([value=""]) {
  color: var(--semantic-color-text-primary);
}


/* Freccia custom per il dropdown */
.select-container::after {
  content: '';
  position: absolute;
  top: 50%;
  right: var(--semantic-size-inset-md);
  transform: translateY(-50%);
  width: 0.8em;
  height: 0.5em;
  background-color: var(--semantic-color-text-tertiary);
  clip-path: polygon(100% 0%, 0 0%, 50% 100%);
  pointer-events: none;
}

/* Stile per lo stato :focus */
.select-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Stile per le opzioni nel dropdown per il tema scuro */
.select-field option {
  background: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}
</style>
