<script setup>
import { computed } from 'vue';
import { useDashboardLayoutStore } from '../../stores/dashboardLayout';

const dashboardLayoutStore = useDashboardLayoutStore();

const availableLayouts = computed(() => {
  const layouts = [{ id: 'custom', name: 'Mio Layout' }];
  for (const templateId in dashboardLayoutStore.templates) {
    layouts.push({
      id: templateId,
      name: dashboardLayoutStore.templates[templateId].name,
    });
  }
  return layouts;
});

const selectedLayout = computed({
  get: () => dashboardLayoutStore.activeLayoutId,
  set: (value) => {
    dashboardLayoutStore.setActiveLayout(value);
  },
});
</script>

<template>
  <div class="layout-selector">
    <label for="layout-select">Layout:</label>
    <select id="layout-select" v-model="selectedLayout">
      <option v-for="layout in availableLayouts" :key="layout.id" :value="layout.id">
        {{ layout.name }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.layout-selector {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}
label {
  font: var(--semantic-font-style-body-md);
  color: var(--semantic-color-text-secondary);
}
select {
  padding: var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-md);
  border: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
  font: var(--semantic-font-style-body-md);
}
</style>
