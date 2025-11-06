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
  />
</template>

<style>
/* Custom styling to match the application's design system */
.multiselect-custom {
  --ms-tag-bg: var(--semantic-color-primary-default);
  --ms-tag-color: var(--semantic-color-primary-text);
  --ms-ring-color: var(--semantic-color-primary-focus);
  --ms-border-color: var(--semantic-color-border);
  --ms-border-width: 1px;
  --ms-radius: 0.25rem;
  --ms-bg: var(--semantic-color-background);
  --ms-color: var(--semantic-color-text); /* Inherited by options, can cause white text */

  /* Dropdown options styling */
  --ms-dropdown-bg: #FFFFFF;
  --ms-option-bg-pointed: #f3f4f6;
  --ms-option-color-pointed: #111827;
  --ms-option-bg-selected: var(--semantic-color-primary-default);
  --ms-option-color-selected: var(--semantic-color-primary-text);
}

/*
  The default option text color is not controlled by a variable.
  This rule sets a dark color for options, overriding the inherited --ms-color.
*/
.multiselect-custom .multiselect-option {
  color: #111827;
}

.multiselect-custom.is-active {
    box-shadow: none;
}
</style>
