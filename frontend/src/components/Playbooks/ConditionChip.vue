<template>
  <div class="condition-chip">
    <span :class="['category-badge', categoryColorClass]">{{ condition.category }}</span>
    <span class="variable-text">{{ condition.variable }}</span>
    <span class="operator-text">{{ operatorMap[condition.operator] || condition.operator }}</span>
    <span class="value-text">{{ condition.value.value }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  condition: {
    type: Object,
    required: true,
  },
});

const operatorMap = {
  EQUALS: '=',
  NOT_EQUALS: '!=',
  GREATER_THAN: '>',
  LESS_THAN: '<',
};

const categoryColorMap = {
  TECHNICAL: 'blue',
  FUNDAMENTAL: 'purple',
  SENTIMENT: 'amber',
  CUSTOM: 'gray',
};

const categoryColorClass = computed(() => {
  const color = categoryColorMap[props.condition.category] || 'gray';
  return `badge-${color}`;
});
</script>

<style scoped>
.condition-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem; /* 8px */
  font-size: 14px;
}
.category-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.badge-blue { background-color: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.badge-purple { background-color: rgba(139, 92, 246, 0.2); color: #c4b5fd; }
.badge-amber { background-color: rgba(245, 158, 11, 0.2); color: #fcd34d; }
.badge-gray { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; }

.variable-text {
  color: #E5E7EB; /* gray-200 */
  font-weight: 500;
}
.operator-text {
  color: #6B7280; /* gray-500 */
  font-size: 12px;
}
.value-text {
  color: #4ade80; /* emerald-400 */
  font-family: monospace;
  font-weight: 700;
}
</style>
