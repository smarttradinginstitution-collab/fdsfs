<script setup>
import { computed } from 'vue';

// --- PROPS ---
const props = defineProps({
  // `modelValue` can now be a Boolean for a single checkbox,
  // or an Array for a group of checkboxes.
  modelValue: {
    type: [Boolean, Array],
    required: true,
  },
  // `value` is the unique value associated with this checkbox instance.
  // It's used when modelValue is an array.
  value: {
    type: [String, Number, Object],
    default: null,
  },
  // `label` is the text to display next to the checkbox.
  label: {
    type: String,
    default: '',
  },
});

// --- EMITS ---
const emit = defineEmits(['update:modelValue']);

// --- COMPUTED ---
// The `checked` state is now computed based on the type of modelValue.
const isChecked = computed(() => {
  if (Array.isArray(props.modelValue)) {
    // If we're in a group, check if our value is in the array.
    return props.modelValue.includes(props.value);
  }
  // Otherwise, it's a single checkbox, so the modelValue is the state.
  return props.modelValue;
});

// --- EVENT HANDLING ---
function updateValue(event) {
  const isChecked = event.target.checked;
  if (Array.isArray(props.modelValue)) {
    // If we are in a group, we need to add/remove the value from the array.
    const currentValue = [...props.modelValue];
    if (isChecked) {
      currentValue.push(props.value);
    } else {
      const index = currentValue.indexOf(props.value);
      if (index > -1) {
        currentValue.splice(index, 1);
      }
    }
    emit('update:modelValue', currentValue);
  } else {
    // If it's a single checkbox, just emit the boolean value.
    emit('update:modelValue', isChecked);
  }
}
</script>

<template>
  <label class="checkbox-wrapper">
    <input
      type="checkbox"
      class="checkbox-hidden"
      :checked="isChecked"
      :value="value"
      @change="updateValue"
    />
    <span class="checkbox-custom"></span>
    <!-- The slot allows for more complex labels than just a string -->
    <span class="checkbox-label">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<style scoped>
.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--base-size-spacing-2);
  cursor: pointer;
  line-height: var(--base-font-line-height-tight);
}

.checkbox-hidden {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-custom {
  display: inline-block;
  width: 1.125rem;
  height: 1.125rem;
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--base-border-radius-sm);
  transition: all var(--base-animation-duration-fast);
  flex-shrink: 0;
}

.checkbox-label {
  color: var(--semantic-color-text-secondary);
  font-size: var(--base-font-size-sm); /* Adjusted for consistency */
}

.checkbox-hidden:checked + .checkbox-custom {
  background-color: var(--semantic-color-interactive-primary-default);
  border-color: var(--semantic-color-interactive-primary-default);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}

.checkbox-hidden:focus-visible + .checkbox-custom {
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}
</style>