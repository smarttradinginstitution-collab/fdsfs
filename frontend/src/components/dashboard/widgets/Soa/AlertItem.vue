<template>
  <div class="alert-item" :title="tooltip">
    <SvgIcon :name="iconName" class="icon" :class="iconClass" />
    <div class="text-content">
      <span class="value">{{ formattedValue }}</span>
      <span class="label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import SvgIcon from '@/components/ui/SvgIcon.vue';

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['autocorrelation', 'drawdown'].includes(value),
  },
  value: {
    type: Number,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  tooltip: {
    type: String,
    default: '',
  },
  threshold: {
    type: Number,
    default: 0.5
  }
});

const iconName = computed(() => {
  return props.type === 'autocorrelation' ? 'brain' : 'graph';
});

const isAlertActive = computed(() => {
    if (props.type === 'drawdown') {
        return props.value > props.threshold;
    }
    return Math.abs(props.value) > props.threshold;
});

const iconClass = computed(() => {
  return {
    'icon-negative': isAlertActive.value,
    'icon-neutral': !isAlertActive.value,
  };
});

const formattedValue = computed(() => {
    if (props.type === 'drawdown') {
        return `Z: ${props.value.toFixed(1)}`;
    }
  return props.value.toFixed(2);
});
</script>

<style scoped>
.alert-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  background-color: #2d3748; /* Gray 800 */
  min-width: 150px;
}

.icon {
  width: 24px;
  height: 24px;
}

.icon-negative {
  color: #f56565; /* Red 400 */
}

.icon-neutral {
  color: #4299e1; /* Blue 400 */
}

.text-content {
  display: flex;
  flex-direction: column;
}

.value {
  font-weight: 600;
  font-size: 1rem;
  color: #fff;
}

.label {
  font-size: 0.75rem;
  color: #a0aec0; /* Cool Gray 400 */
}
</style>
