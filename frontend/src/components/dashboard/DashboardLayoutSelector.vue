<script setup>
import { computed } from 'vue';
import { useDashboardLayoutStore } from '../../stores/dashboardLayoutStore';
import BaseSelect from '../ui/BaseSelect.vue';

const layoutStore = useDashboardLayoutStore();

const availableLayouts = computed(() => layoutStore.availableLayouts);

const selectedLayoutId = computed({
  get: () => layoutStore.currentLayoutId,
  set: (value) => {
    layoutStore.selectLayout(value);
  },
});

const options = computed(() =>
  availableLayouts.value.map(layout => ({
    value: layout.id,
    label: layout.name,
  }))
);
</script>

<template>
  <div class="layout-selector">
    <BaseSelect
      v-model="selectedLayoutId"
      :options="options"
      label="Seleziona Layout"
      id="layout-select"
    />
  </div>
</template>

<style scoped>
.layout-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
}
</style>
