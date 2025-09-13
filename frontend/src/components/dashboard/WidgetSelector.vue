<script setup>
import { computed } from 'vue';
import { useDashboardLayoutStore } from '../../stores/dashboardLayout';
import BaseButton from '../ui/BaseButton.vue';

const props = defineProps({
  zone: {
    type: String,
    required: true,
  },
  allowedWidgets: {
    type: Array,
    required: true,
  },
});

const dashboardLayoutStore = useDashboardLayoutStore();
const emit = defineEmits(['addWidget']);

const availableWidgets = computed(() => {
  // Get the full widget details from the store's master list
  const allWidgets = dashboardLayoutStore.availableWidgets;

  return props.allowedWidgets.map(widgetKey => {
    const widgetDetails = allWidgets.find(w => w.i === widgetKey);
    const isActive = dashboardLayoutStore.layout[props.zone]?.some(w => w.i === widgetKey);
    return {
      ...widgetDetails,
      isActive: !!isActive,
    };
  });
});

const handleAddWidget = (widgetId) => {
  emit('addWidget', { zone: props.zone, widgetId });
};
</script>

<template>
  <div class="widget-selector">
    <h4>Aggiungi Widget</h4>
    <ul>
      <li v-for="widget in availableWidgets" :key="widget.i">
        <span>{{ widget.name }}</span>
        <BaseButton
          @click="handleAddWidget(widget.i)"
          :disabled="widget.isActive"
          size="small"
        >
          Aggiungi
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
