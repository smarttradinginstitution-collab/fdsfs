<script setup>
import { computed } from 'vue';
import draggable from 'vuedraggable';
import { useUiStore } from '../../../stores/uiStore';
import { useTradesStore } from '../../../stores/trades';
import StatCard from '../widgets/StatCard/index.vue';
import PlusIcon from '../../icons/PlusIcon.vue';

const uiStore = useUiStore();
const tradesStore = useTradesStore();

const isEditing = computed(() => uiStore.isLayoutEditing);

const onStatsDragEnd = (event) => {
  uiStore.moveStat({
    oldIndex: event.oldIndex,
    newIndex: event.newIndex,
  });
};
</script>

<template>
  <div class="grid-zone-wrapper">
    <draggable
      :list="uiStore.visibleStatKeys"
      item-key="key"
      tag="div"
      class="stats-grid"
      ghost-class="ghost"
      @end="onStatsDragEnd"
      :disabled="!isEditing"
    >
      <template #item="{ element: statKey }">
        <div class="widget-wrapper" :class="{ 'is-editing': isEditing }">
          <StatCard :stat="tradesStore.allDashboardStats[statKey]" />
          <button
            v-if="isEditing"
            class="remove-widget-btn"
            @click="uiStore.toggleStatVisibility(statKey)"
          >
            &times;
          </button>
        </div>
      </template>
      <template #footer>
        <button v-if="isEditing" @click="uiStore.toggleStatSelector" class="add-widget-button">
          <PlusIcon /> Aggiungi o Rimuovi Stat
        </button>
      </template>
    </draggable>
  </div>
</template>

<style lang="scss" scoped>
/*
  Gli stili per la griglia (.stats-grid) sono stati centralizzati in DashboardView.vue
  per garantire una gestione unica e coerente del layout responsive.
  Questo file contiene solo stili specifici per gli elementi interni alla zona.
*/

.ghost {
  opacity: 0.5;
  background-color: var(--semantic-color-surface-secondary);
}

.widget-wrapper {
  position: relative;
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
