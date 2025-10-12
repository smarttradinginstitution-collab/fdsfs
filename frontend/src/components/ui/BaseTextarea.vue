<script setup>
import { ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';

const textareaElement = ref(null);
const uniqueId = ref(`textarea-${uuidv4()}`);

defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  rows: {
    type: Number,
    default: 3,
  },
});

const emit = defineEmits(['update:modelValue']);

function onInput(event) {
  emit('update:modelValue', event.target.value);
}

defineExpose({
  focus: () => {
    textareaElement.value?.focus();
  },
});
</script>

<template>
  <div class="textarea-wrapper">
    <label v-if="label" :for="uniqueId" class="textarea-label">{{ label }}</label>
    <textarea
      :id="uniqueId"
      ref="textareaElement"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :rows="rows"
      class="textarea-field"
      @input="onInput"
    ></textarea>
  </div>
</template>

<style scoped>
.textarea-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;
}

.textarea-label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

.textarea-field {
  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-base-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  transition: box-shadow var(--base-animation-duration-fast), border-color var(--base-animation-duration-fast);
  resize: vertical; /* Allow vertical resizing */
}

.textarea-field::placeholder {
  color: var(--semantic-color-text-tertiary);
}

.textarea-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

.textarea-field:disabled {
  background-color: var(--semantic-color-surface-disabled);
  color: var(--semantic-color-text-disabled);
  cursor: not-allowed;
}
</style>