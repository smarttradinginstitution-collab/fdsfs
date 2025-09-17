<script setup>
import { computed, ref } from 'vue';
import { useTradesStore } from '../../../stores/trades';
import { useUiStore } from '../../../stores/uiStore';
import BaseCheckbox from '../../ui/BaseCheckbox.vue';
import ChevronDownIcon from '../../icons/ChevronDownIcon.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();

const allStats = computed(() => tradesStore.allDashboardStats);

const groupedStats = computed(() => {
  const groups = {};
  for (const key in allStats.value) {
    const stat = allStats.value[key];
    if (!groups[stat.category]) {
      groups[stat.category] = [];
    }
    groups[stat.category].push(stat);
  }
  return groups;
});

const openCategories = ref(['Profitability']); // Open 'Profitability' by default

const toggleCategory = (category) => {
  const index = openCategories.value.indexOf(category);
  if (index === -1) {
    openCategories.value.push(category);
  } else {
    openCategories.value.splice(index, 1);
  }
};

const handleCheckboxChange = (statKey) => {
  uiStore.toggleStatVisibility(statKey);
};
</script>

<template>
  <div class="stat-selector-menu">
    <div v-for="(stats, category) in groupedStats" :key="category" class="category-group">
      <button @click="toggleCategory(category)" class="category-header">
        <span>{{ category }}</span>
        <ChevronDownIcon :class="{ 'rotate-180': openCategories.includes(category) }" />
      </button>
      <div v-if="openCategories.includes(category)" class="category-content">
        <div v-for="stat in stats" :key="stat.key" class="selector-item">
          <BaseCheckbox
            :label="stat.label"
            :model-value="uiStore.visibleStatKeys.includes(stat.key)"
            @update:modelValue="handleCheckboxChange(stat.key)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-selector-menu {
  padding: var(--semantic-size-inset-sm);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  min-width: 280px;
}

.category-group {
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-subtle);
}
.category-group:last-child {
  border-bottom: none;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: var(--semantic-size-inset-sm);
  font: var(--semantic-font-style-label-md);
  cursor: pointer;
  background-color: transparent;
  border: none;
  color: var(--semantic-color-text-primary);
  border-radius: var(--semantic-border-radius-md);
}
.category-header:hover {
  background-color: var(--semantic-color-surface-secondary-hover);
}

.category-header svg {
  width: var(--base-size-spacing-4);
  height: var(--base-size-spacing-4);
  transition: transform 0.2s ease-in-out;
}
.category-header .rotate-180 {
  transform: rotate(180deg);
}

.category-content {
  padding: var(--semantic-size-inset-md);
  padding-top: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--semantic-size-stack-md);
}

.selector-item {
  /* Add any specific styling for the items if needed */
}
</style>
