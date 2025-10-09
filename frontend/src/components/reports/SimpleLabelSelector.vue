<template>
  <div class="simple-label-selector">
    <PopoverMenu>
      <template #trigger="{ toggle }">
        <button @click="toggle" class="selector-trigger" type="button">
          <div v-if="selectedItems.length === 0" class="placeholder">{{ placeholder }}</div>
          <div v-else class="pills-container">
            <BasePill
              v-for="item in selectedItems"
              :key="item.id"
              :style="{ backgroundColor: item.color, color: getTextColor(item.color) }"
              class="trigger-pill"
            >
              {{ item.name }}
            </BasePill>
          </div>
          <ChevronDownIcon class="trigger-icon" />
        </button>
      </template>

      <template #content>
        <div class="popover-content">
          <div class="search-bar">
            <BaseInput v-model="searchTerm" :placeholder="`Search ${itemTypeName.toLowerCase()}s...`" class="search-input" />
          </div>
          <div class="items-list">
            <div v-if="filteredItems.length === 0" class="no-results">
              No {{ itemTypeName.toLowerCase() }}s found.
            </div>
            <BaseCheckbox
              v-for="item in filteredItems"
              :key="item.id"
              :model-value="isSelected(item.id)"
              :label="item.name"
              @update:modelValue="toggleItem(item.id)"
              class="item-checkbox"
            />
          </div>
        </div>
      </template>
    </PopoverMenu>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import PopoverMenu from '@/components/ui/PopoverMenu.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';
import { ChevronDownIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  modelValue: { type: Array, default: () => [] }, // Array of selected IDs
  allItems: { type: Array, required: true }, // Array of all available item objects { id, name, color }
  placeholder: { type: String, default: 'Select items...' },
  itemTypeName: { type: String, default: 'Item' },
});
const emit = defineEmits(['update:modelValue']);

const searchTerm = ref('');

const filteredItems = computed(() => {
  if (!searchTerm.value) return props.allItems;
  const lowerCaseSearch = searchTerm.value.toLowerCase();
  return props.allItems.filter(item => item.name.toLowerCase().includes(lowerCaseSearch));
});

const selectedItems = computed(() => {
  return props.allItems.filter(item => props.modelValue.includes(item.id));
});

const isSelected = (itemId) => props.modelValue.includes(itemId);

const toggleItem = (itemId) => {
  const newSelection = [...props.modelValue];
  const index = newSelection.indexOf(itemId);
  if (index > -1) {
    newSelection.splice(index, 1);
  } else {
    newSelection.push(itemId);
  }
  emit('update:modelValue', newSelection); // This enables auto-save
};

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};
</script>

<style scoped>
.selector-trigger {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  text-align: left; cursor: pointer; min-height: 38px;
}
.placeholder { color: var(--semantic-color-text-placeholder); }
.pills-container { display: flex; flex-wrap: wrap; gap: var(--semantic-size-stack-xs); flex-grow: 1; }
.trigger-pill { font-size: var(--semantic-font-style-body-sm); padding: 2px 8px; }
.trigger-icon { width: 1.25rem; height: 1.25rem; color: var(--semantic-color-text-secondary); margin-left: var(--semantic-size-stack-sm); flex-shrink: 0; }
.popover-content { display: flex; flex-direction: column; width: 300px; }
.search-bar { padding: var(--semantic-size-inset-sm); border-bottom: 1px solid var(--semantic-color-border-default); }
.search-input { width: 100%; }
.items-list { max-height: 300px; overflow-y: auto; padding: var(--semantic-size-inset-sm); display: flex; flex-direction: column; gap: var(--semantic-size-stack-xxs); }
.item-checkbox { padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm); cursor: pointer; border-radius: var(--semantic-border-radius-interactive); }
.item-checkbox:hover { background-color: var(--semantic-color-surface-hover); }
.no-results { padding: var(--semantic-size-inset-lg); text-align: center; color: var(--semantic-color-text-secondary); }
</style>