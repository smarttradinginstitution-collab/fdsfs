<template>
  <li class="rule-item">
    <div class="rule-content">
      <component :is="iconComponent" :class="iconClass" class="status-icon" />
      <span class="rule-label">{{ rule.name }}</span>
    </div>
    <span class="status-text">{{ statusText }}</span>
  </li>
</template>

<script setup>
import { computed } from 'vue';
import { CheckCircleIcon, XCircleIcon, MinusCircleIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
});

const iconComponent = computed(() => {
  switch (props.rule.status) {
    case 'completed':
      return CheckCircleIcon;
    case 'failed':
      return XCircleIcon;
    default:
      return MinusCircleIcon; // Or another appropriate default icon
  }
});

const iconClass = computed(() => {
  return {
    'icon-success': props.rule.status === 'completed',
    'icon-danger': props.rule.status === 'failed',
    'icon-neutral': props.rule.status !== 'completed' && props.rule.status !== 'failed',
  };
});

// Helper function to format currency
const formatCurrency = (value) => {
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  return `$${value}`;
};


const statusText = computed(() => {
  const stats = props.rule.statistics;
  if (!stats) return '';

  switch (props.rule.code) {
    case 'MAX_LOSS_PER_DAY':
    case 'MAX_LOSS_PER_TRADE':
        return `${formatCurrency(stats.current_value)} / ${formatCurrency(stats.target_value)}`;
    case 'START_MY_DAY_BY':
      // Assuming 'current_value' is a timestamp or null
      const currentTime = stats.current_value ? new Date(stats.current_value).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' }) : 'None';
      const targetTime = new Date(stats.target_value).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
      return `${currentTime} / ${targetTime}`;
    default:
      return `${stats.current_value} / ${stats.target_value}`;
  }
});

</script>

<style scoped>
.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-sm) 0;
}

.rule-content {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
}

.status-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.icon-success {
  color: var(--semantic-color-feedback-positive-icon);
}

.icon-danger {
  color: var(--semantic-color-feedback-danger-icon);
}

.icon-neutral {
  color: var(--semantic-color-text-tertiary);
}

.rule-label {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
}

.status-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-tertiary);
}
</style>