<template>
  <div class="multiselect-container" ref="containerRef">
    <div class="selected-items-wrapper" @click="toggleDropdown">
      <div v-if="selectedOptions.length === 0" class="placeholder">{{ placeholder }}</div>
      <div v-else class="pills-container">
        <BasePill v-for="option in selectedOptions" :key="option.value" class="pill">
          {{ option.label }}
          <span class="remove-pill" @click.stop="removeOption(option)">&times;</span>
        </BasePill>
      </div>
      <span class="chevron" :class="{ 'is-open': isOpen }">&#9662;</span>
    </div>
    <div v-if="isOpen" class="options-list">
      <div
        v-for="option in options"
        :key="option.value"
        class="option-item"
        :class="{ 'is-selected': isSelected(option) }"
        @click="toggleOption(option)"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import BasePill from './BasePill.vue';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  options: {
    type: Array,
    required: true, // expecting [{ value: '...', label: '...' }]
  },
  placeholder: {
    type: String,
    default: 'Select options...',
  },
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const containerRef = ref(null);

const selectedValues = ref([...props.modelValue]);

const selectedOptions = computed(() => {
  return props.options.filter(opt => selectedValues.value.includes(opt.value));
});

const isSelected = (option) => {
  return selectedValues.value.includes(option.value);
};

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
};

const toggleOption = (option) => {
  const index = selectedValues.value.indexOf(option.value);
  if (index > -1) {
    selectedValues.value.splice(index, 1);
  } else {
    selectedValues.value.push(option.value);
  }
};

const removeOption = (option) => {
  const index = selectedValues.value.indexOf(option.value);
  if (index > -1) {
    selectedValues.value.splice(index, 1);
  }
};

watch(selectedValues, (newValue) => {
  emit('update:modelValue', newValue);
});

watch(() => props.modelValue, (newValue) => {
  if (JSON.stringify(newValue) !== JSON.stringify(selectedValues.value)) {
    selectedValues.value = [...newValue];
  }
});

const handleClickOutside = (event) => {
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    closeDropdown();
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.multiselect-container {
  position: relative;
  width: 100%;
}
.selected-items-wrapper {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: var(--semantic-size-inset-sm);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  min-height: 38px; /* Match BaseInput height */
}
.placeholder {
  color: var(--semantic-color-text-placeholder);
  padding: 4px;
}
.pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
}
.pill {
  display: flex;
  align-items: center;
  padding-right: 8px;
}
.remove-pill {
  margin-left: 8px;
  cursor: pointer;
  font-weight: bold;
}
.chevron {
  margin-left: auto;
  color: var(--semantic-color-text-secondary);
  transition: transform 0.2s;
}
.chevron.is-open {
  transform: rotate(180deg);
}
.options-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}
.option-item {
  padding: var(--semantic-size-inset-md);
  cursor: pointer;
}
.option-item:hover {
  background-color: var(--semantic-color-surface-secondary);
}
.option-item.is-selected {
  background-color: var(--semantic-color-surface-brand);
  color: var(--semantic-color-text-on-brand);
}
</style>