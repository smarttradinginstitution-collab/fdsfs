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
  --ms-color: var(--semantic-color-text);
}

.multiselect-custom.is-active {
    box-shadow: none;
}
</style>
