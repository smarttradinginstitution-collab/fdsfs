<template>
  <div class="toolbar-dropdown" ref="dropdownRef">
    <button @click="toggle" class="dropdown-toggle">
      <span>{{ selectedLabel }}</span>
      <ChevronDownIcon class="h-4 w-4" />
    </button>
    <div v-if="isOpen" class="dropdown-menu">
      <button
        v-for="item in items"
        :key="item.value"
        @click="selectItem(item)"
        class="dropdown-item"
        :class="{ 'is-active': item.isActive ? item.isActive() : false }"
      >
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { ChevronDownIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: [String, Number],
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const dropdownRef = ref(null);

const selectedLabel = computed(() => {
  const selected = props.items.find(item => item.value === props.modelValue);
  return selected ? selected.label : props.items[0]?.label || 'Select';
});

const toggle = () => {
  isOpen.value = !isOpen.value;
};

const selectItem = (item) => {
  emit('update:modelValue', item.value);
  isOpen.value = false;
};

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style lang="scss" scoped>
.toolbar-dropdown {
  position: relative;
  display: inline-block;
  margin: 0 0.1rem;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.5rem;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: var(--semantic-color-text-primary);
  cursor: pointer;
  font-size: 0.875rem;

  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
  }
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 10;
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: 4px;
  min-width: 150px;
  padding: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.5rem;
  background: none;
  border: none;
  color: var(--semantic-color-text-primary);
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.875rem;

  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
  }

  &.is-active {
    background-color: var(--semantic-color-surface-secondary);
    font-weight: 600;
  }
}
</style>