<script setup>
import { computed } from 'vue';
import { useDashboardLayoutStore } from '../../stores/dashboardLayout';
import BaseButton from '../ui/BaseButton.vue';

const dashboardLayoutStore = useDashboardLayoutStore();

const emit = defineEmits(['addWidget', 'removeWidget']);

const widgets = computed(() => {
  return dashboardLayoutStore.availableWidgets.map(widget => ({
    ...widget,
    isActive: dashboardLayoutStore.layout.some(layoutWidget => layoutWidget.i === widget.i),
  }));
});

const toggleWidget = (widget) => {
  if (widget.isActive) {
    emit('removeWidget', widget.i);
  } else {
    emit('addWidget', widget.i);
  }
};
</script>

<template>
  <div class="widget-selector">
    <h4>Available Widgets</h4>
    <ul>
      <li v-for="widget in widgets" :key="widget.i">
        <span>{{ widget.name }}</span>
        <BaseButton @click="toggleWidget(widget)" :variant="widget.isActive ? 'secondary' : 'primary'">
          {{ widget.isActive ? 'Remove' : 'Add' }}
        </BaseButton>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.widget-selector {
  padding: var(--semantic-size-inset-md);
  min-width: 250px;
}
h4 {
  margin-top: 0;
  margin-bottom: var(--semantic-size-stack-md);
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
li {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
