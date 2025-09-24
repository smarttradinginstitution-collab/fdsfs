<script setup>
import { computed } from 'vue';
import draggable from 'vuedraggable';
import { useUiStore } from '../../../stores/uiStore';
import PopoverMenu from '../../ui/PopoverMenu.vue';
import WidgetSelector from '../WidgetSelector.vue';
import PlusIcon from '../../icons/PlusIcon.vue';

const props = defineProps({
  zoneId: {
    type: String,
    required: true,
  },
  widgets: {
    type: Array,
    required: true,
  },
  widgetComponents: {
    type: Object,
    required: true,
  },
  gridClass: {
    type: String,
    default: '',
  },
  maxItems: {
    type: Number,
    default: Infinity,
  },
  allowedWidgets: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['update:widgets', 'add-widget', 'remove-widget', 'drag-end']);

const uiStore = useUiStore();

const draggableList = computed({
  get: () => props.widgets,
  set: (value) => {
    emit('update:widgets', value);
  },
});

const isEditing = computed(() => uiStore.isLayoutEditing);

const handleDragEnd = (event) => {
  emit('drag-end', { zone: props.zoneId, event });
};

const handleAddWidget = (payload) => {
  emit('add-widget', payload);
};

const handleRemoveWidget = (widgetId) => {
  emit('remove-widget', { zone: props.zoneId, widgetId });
};
</script>

<template>
  <div class="grid-zone-wrapper">
    <draggable
      v-model="draggableList"
      item-key="i"
      tag="div"
      :class="['widget-grid', gridClass]"
      ghost-class="ghost"
      @end="handleDragEnd"
      :disabled="!isEditing"
    >
      <template #item="{ element: widget }">
        <div class="widget-wrapper" :class="{ 'is-editing': isEditing }">
          <component :is="widgetComponents[widget.i]" />
          <button
            v-if="isEditing"
            class="remove-widget-btn"
            @click="handleRemoveWidget(widget.i)"
          >
            &times;
          </button>
        </div>
      </template>
      <template #footer>
        <div
          class="add-widget-wrapper"
          v-if="isEditing && widgets.length < maxItems"
        >
          <PopoverMenu>
            <template #trigger="{ toggle }">
              <button @click="toggle" class="add-widget-button">
                <PlusIcon /> Aggiungi Widget
              </button>
            </template>
            <template #content="{ close }">
              <WidgetSelector
                :zone="zoneId"
                :allowed-widgets="allowedWidgets"
                @add-widget="handleAddWidget($event); close()"
              />
            </template>
          </PopoverMenu>
        </div>
      </template>
    </draggable>
  </div>
</template>

<style scoped>
/* Styles are intentionally kept minimal as they will be inherited from the parent or global styles */
.widget-grid {
  display: grid;
  gap: var(--semantic-size-stack-lg);
  min-width: 0; /* Fix for grid inside flexbox overflow */
}

.ghost {
  opacity: 0.5;
  background-color: var(--semantic-color-surface-secondary);
}

.widget-wrapper {
  position: relative;
  /* This is the key to preventing grid blowouts. It allows the widget
     to shrink below its content's intrinsic minimum size. The overflow
     will then be handled by the BaseWidget's own scrolling content area. */
  min-width: 0;
}

.widget-wrapper.is-editing {
  cursor: grab;
}

.widget-wrapper.is-editing:active {
  cursor: grabbing;
}

.remove-widget-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  line-height: 1;
  transition: background-color 0.2s;
}

.remove-widget-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.add-widget-button {
  background-color: var(--semantic-color-surface-primary);
  border: 2px dashed var(--semantic-color-border-default);
  color: var(--semantic-color-text-secondary);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  cursor: pointer;
  width: 100%;
  min-height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  transition: all 0.2s;
}

.add-widget-button:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
  border-color: var(--semantic-color-border-focus);
}
</style>
