<script setup>
import { computed } from 'vue';
import { useUiStore } from '../../../stores/uiStore';
import { useTradesStore } from '../../../stores/trades';
import CloseIcon from '@/components/icons/CloseIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';

defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const uiStore = useUiStore();
const tradesStore = useTradesStore();

const allStats = computed(() => tradesStore.allDashboardStats);

const groupedStats = computed(() => {
  const groups = {
    'Profitability': [],
    'Ratios & Efficiency': [],
    'Risk Management': [],
    'Consistency': [],
    'Other': [],
  };

  for (const key in allStats.value) {
    const stat = allStats.value[key];
    if (groups[stat.category]) {
      groups[stat.category].push(stat);
    } else {
      groups['Other'].push(stat);
    }
  }
  return groups;
});

const isVisible = (statKey) => {
  return uiStore.visibleStatKeys.includes(statKey);
};
</script>

<template>
  <div class="stat-selector-panel" :class="{ 'is-open': isOpen }">
    <div class="panel-header">
      <h3 class="panel-title">Manage Stats</h3>
      <IconButton @click="uiStore.closeStatSelector()" aria-label="Close panel">
        <CloseIcon />
      </IconButton>
    </div>
    <div class="panel-content">
      <div v-for="(stats, category) in groupedStats" :key="category" class="stat-group">
        <h4 class="group-title">{{ category }}</h4>
        <ul class="stat-list">
          <li
            v-for="stat in stats"
            :key="stat.key"
            @click="uiStore.toggleStatVisibility(stat.key)"
            class="stat-item"
            :class="{ 'is-visible': isVisible(stat.key) }"
          >
            <div class="checkbox">
              <div class="checkbox-inner"></div>
            </div>
            <span class="stat-name">{{ stat.label }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base Styles for the Panel */
.stat-selector-panel {
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
  transition: transform 0.3s var(--semantic-animation-easing-emphasized);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
  flex-shrink: 0;
}

.panel-title {
  font: var(--semantic-font-style-heading-lg);
}

.panel-content {
  padding: var(--semantic-size-inset-lg);
  overflow-y: auto;
  flex-grow: 1;
}

.stat-group {
  margin-bottom: var(--semantic-size-stack-lg);
}

.group-title {
  font: var(--semantic-font-style-label-lg);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-sm);
}

.stat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.2s;
}

.stat-item:hover {
  background-color: var(--semantic-color-surface-secondary);
}

.stat-name {
  font: var(--semantic-font-style-body-md);
}

/* Checkbox Styles */
.checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s, border-color 0.2s;
}
.checkbox-inner {
  width: 12px;
  height: 12px;
  background-color: white;
  border-radius: 2px;
  transform: scale(0);
  transition: transform 0.2s;
}
.stat-item.is-visible .checkbox {
  background-color: var(--semantic-color-interactive-primary-default);
  border-color: var(--semantic-color-interactive-primary-default);
}
.stat-item.is-visible .checkbox-inner {
  transform: scale(1);
}

/* --- Responsive Layouts --- */

/* Desktop: Sidebar */
@include media-up('md') {
  .stat-selector-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 320px;
    height: 100vh;
    transform: translateX(100%);
  }

  .stat-selector-panel.is-open {
    transform: translateX(0);
  }
}

/* Mobile: Bottom Sheet */
@include media-down('md') {
  .stat-selector-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 80vh; /* Limit height to 80% of viewport */
    border-top-left-radius: var(--semantic-border-radius-xl);
    border-top-right-radius: var(--semantic-border-radius-xl);
    transform: translateY(100%);
  }

  .stat-selector-panel.is-open {
    transform: translateY(0);
  }
}
</style>