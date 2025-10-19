<template>
  <div class="rules-table-container">
    <div class="table-header">
      <h3 class="table-title">Current Rules</h3>
      <BaseButton @click="$emit('edit-rules')" variant="primary" size="medium" :disabled="isLoading">
        Edit Rules
      </BaseButton>
    </div>
    <div class="table-wrapper">
      <table class="rules-table">
        <thead>
          <tr>
            <th>RULE</th>
            <th>CONDITION</th>
            <th>AVG PERFORMANCE</th>
            <th>FOLLOW RATE</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="rules.length === 0">
            <td colspan="4" class="empty-state">No rules defined yet.</td>
          </tr>
          <tr v-for="rule in rules" :key="rule.id">
            <td>
              <div class="rule-name">{{ rule.name }}</div>
            </td>
            <td>
              <span class="condition">{{ formatCondition(rule) }}</span>
            </td>
            <td>
              <span class="avg-performance">{{ formatAvgPerformance(rule) }}</span>
            </td>
            <td>
              <span class="follow-rate">{{ rule.follow_rate ? rule.follow_rate.toFixed(1) + '%' : '-' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue';

defineProps({
  rules: {
    type: Array,
    required: true,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['edit-rules']);

function formatCondition(rule) {
  if (rule.isManual || !rule.settings) {
    return '-';
  }

  const { settings } = rule;
  switch (rule.name) {
    case 'Start my day by':
      return settings.start_day_by || '-';
    case 'Link trades to playbook':
      return `${settings.link_trades_to_playbook_threshold || 0}%`;
    case 'Trade has stop loss':
      return `${settings.trade_has_stop_loss_threshold || 0}%`;
    case 'Max loss per trade':
      if (settings.max_loss_per_trade_type === '%') {
        return `${settings.max_loss_per_trade_value || 0}%`;
      }
      return `$${settings.max_loss_per_trade_value || 0}`;
    case 'Max loss per day':
      return `$${settings.max_loss_per_day || 0}`;
    default:
      return '-';
  }
}

function formatAvgPerformance(rule) {
    if (rule.isManual || rule.avg_performance === 'N/A') {
        return '-';
    }

    const value = parseFloat(rule.avg_performance);

    if (rule.name === 'Link trades to playbook' || rule.name === 'Trade has stop loss') {
        return `${value.toFixed(1)}%`;
    }

    if (rule.name === 'Max loss per day') {
        return `$${value.toFixed(2)}`;
    }

    return value;
}
</script>

<style scoped>
.rules-table-container {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-stack-md);
}

.table-title {
  font: var(--semantic-font-style-heading-lg);
}

.table-wrapper {
  overflow-x: auto;
}

.rules-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

th, td {
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-sm);
  text-align: left;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

th {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase;
}

.rule-name {
  font: var(--semantic-font-style-body-base);
  font-weight: var(--base-font-weight-medium);
  color: var(--semantic-color-text-primary);
}

.condition {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-base);
}
</style>