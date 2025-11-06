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
        <option v-if="!multiple && placeholder" value="">
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

.select-field {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  cursor: pointer;

  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-base-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  padding-right: var(--semantic-size-inset-xl);
  transition: box-shadow var(--base-animation-duration-fast),
    border-color var(--base-animation-duration-fast);
}

/* freccia custom */
.select-container::after {
  content: '';
  position: absolute;
  top: 50%;
  right: var(--semantic-size-inset-md);
  transform: translateY(-50%);
  width: 1em;
  height: 1em;
  background-color: var(--semantic-color-text-tertiary);
  clip-path: polygon(100% 25%, 50% 75%, 0 25%);
  pointer-events: none;
  transition: background-color var(--base-animation-duration-fast);
}

.select-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* 👇 per quando il browser apre il menu in tema scuro */
.select-field option {
  background: #ffffff;
  color: #111827;
}
</style>
