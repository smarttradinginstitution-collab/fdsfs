
<template>
  <div class="multiselect-wrapper">
    <label v-if="label" class="multiselect-label">{{ label }}</label>
    <VueMultiselect
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
      :options="options"
      :multiple="true"
      :taggable="true"
      @tag="addTag"
      :placeholder="placeholder"
      label="text"
      track-by="value"
    />
  </div>
</template>

<script setup>
import VueMultiselect from 'vue-multiselect';

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

const emit = defineEmits(['update:modelValue', 'tag']);

const addTag = (newTag) => {
  // Emitting a custom event to handle tag creation if needed
  emit('tag', newTag);
};
</script>

<style lang="scss">
/* Stile per adattarsi al design system */
.multiselect-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;

  .multiselect-label {
    font-family: var(--semantic-font-style-label-md-font-family);
    font-size: var(--semantic-font-style-label-md-font-size);
    font-weight: var(--semantic-font-style-label-md-font-weight);
    color: var(--semantic-color-text-secondary);
  }
}

.multiselect {
  .multiselect__tags {
    background-color: var(--semantic-color-surface-primary);
    border: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    padding: var(--semantic-size-inset-sm);
    min-height: 40px; /* Altezza simile a BaseInput */
  }

  .multiselect__tag {
    background-color: var(--semantic-color-surface-accent);
    color: var(--semantic-color-text-on-brand);
    border-radius: var(--semantic-border-radius-pill);
  }

  .multiselect__tag-icon::after {
    color: var(--semantic-color-text-on-brand);
  }

  .multiselect__input, .multiselect__single {
    background-color: transparent;
    color: var(--semantic-color-text-primary);
  }

  .multiselect__content-wrapper {
    background-color: var(--semantic-color-surface-primary);
    border: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-top: none;
  }

  .multiselect__option--highlight {
    background-color: var(--semantic-color-surface-accent);
    color: var(--semantic-color-text-on-brand);
  }

  .multiselect__option--selected {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    font-weight: 600;
  }
}
</style>
