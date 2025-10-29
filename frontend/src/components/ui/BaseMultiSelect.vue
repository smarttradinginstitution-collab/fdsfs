
<template>
  <div class="multiselect-wrapper">
    <label v-if="label" class="multiselect-label">{{ label }}</label>
    <Multiselect
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
      :options="options"
      mode="tags"
      :searchable="true"
      :placeholder="placeholder"
      :close-on-select="false"
    />
  </div>
</template>

<script setup>
import Multiselect from '@vueform/multiselect';

defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select options'
  }
});

const emit = defineEmits(['update:modelValue']);
</script>

<!-- Import global styles for @vueform/multiselect -->
<style src="@vueform/multiselect/themes/default.css"></style>

<style lang="scss">
/* Stile per adattarsi al design system (variabili --ms-*) */
.multiselect-wrapper {
  --ms-bg: var(--semantic-color-surface-primary);
  --ms-border-color: var(--semantic-color-border-default);
  --ms-border-radius: var(--semantic-border-radius-interactive);
  --ms-ring-color: transparent; // No focus ring, use box-shadow
  --ms-placeholder-color: var(--semantic-color-text-placeholder);
  --ms-font-size: var(--semantic-font-style-body-base-font-size);
  --ms-line-height: 1.4;

  --ms-tag-bg: var(--semantic-color-surface-accent);
  --ms-tag-color: var(--semantic-color-text-on-brand);
  --ms-tag-radius: var(--semantic-border-radius-pill);

  --ms-dropdown-bg: var(--semantic-color-surface-primary);
  --ms-dropdown-border-color: var(--semantic-color-border-default);

  --ms-option-bg-pointed: var(--semantic-color-surface-accent);
  --ms-option-color-pointed: var(--semantic-color-text-on-brand);
  --ms-option-bg-selected: var(--semantic-color-surface-secondary);
  --ms-option-color-selected: var(--semantic-color-text-primary);

  .multiselect-label {
    font-family: var(--semantic-font-style-label-md-font-family);
    font-size: var(--semantic-font-style-label-md-font-size);
    font-weight: var(--semantic-font-style-label-md-font-weight);
    color: var(--semantic-color-text-secondary);
    margin-bottom: var(--semantic-size-stack-xs);
  }

  .multiselect.is-active {
     box-shadow: var(--semantic-effect-shadow-focus-ring);
  }
}
</style>
