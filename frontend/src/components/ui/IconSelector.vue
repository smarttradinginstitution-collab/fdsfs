<script setup>
import { defineProps, defineEmits, shallowRef } from 'vue';

// Import a selection of available icons
import BuildingLibraryIcon from '@/components/icons/BuildingLibraryIcon.vue';
import CalendarIcon from '@/components/icons/CalendarIcon.vue';
import SparkleIcon from '@/components/icons/SparkleIcon.vue';
import SunIcon from '@/components/icons/SunIcon.vue';
import MoonIcon from '@/components/icons/MoonIcon.vue';
import FilterIcon from '@/components/icons/FilterIcon.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import SettingsIcon from '@/components/icons/SettingsIcon.vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: 'BuildingLibraryIcon',
  },
});

const emit = defineEmits(['update:modelValue']);

const icons = shallowRef([
  { name: 'BuildingLibraryIcon', component: BuildingLibraryIcon },
  { name: 'CalendarIcon', component: CalendarIcon },
  { name: 'SparkleIcon', component: SparkleIcon },
  { name: 'SunIcon', component: SunIcon },
  { name: 'MoonIcon', component: MoonIcon },
  { name: 'FilterIcon', component: FilterIcon },
  { name: 'PlusIcon', component: PlusIcon },
  { name: 'SettingsIcon', component: SettingsIcon },
]);

const selectIcon = (iconName) => {
  emit('update:modelValue', iconName);
};
</script>

<template>
  <div class="icon-selector">
    <div
      v-for="icon in icons"
      :key="icon.name"
      class="icon-option"
      :class="{ 'is-selected': modelValue === icon.name }"
      @click="selectIcon(icon.name)"
      role="radio"
      :aria-checked="modelValue === icon.name"
      :aria-label="`Icon ${icon.name}`"
    >
      <component :is="icon.component" class="icon-svg" />
    </div>
  </div>
</template>

<style scoped>
.icon-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}

.icon-option {
  width: 32px;
  height: 32px;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  border: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--semantic-color-text-secondary);
}

.icon-option:hover {
  background-color: var(--semantic-color-surface-hover);
  color: var(--semantic-color-text-primary);
}

.icon-option.is-selected {
  border-color: var(--semantic-color-primary-default);
  background-color: var(--semantic-color-primary-default);
  color: var(--semantic-color-text-on-primary);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
}

.icon-svg {
  width: 18px;
  height: 18px;
}
</style>