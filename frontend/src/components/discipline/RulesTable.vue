<template>
  <div class="rules-table-container">
    <div class="table-header">
      <h3 class="table-title">Current Rules</h3>
      <BaseButton @click="$emit('edit-rules')" variant="primary" size="medium">
        Edit Rules
      </BaseButton>
    </div>
    <div class="table-wrapper">
      <table class="rules-table">
        <thead>
          <tr>
            <th>RULE & CONDITION</th>
            <th>FOLLOW RATE</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="rules.length === 0">
            <td colspan="2" class="empty-state">No rules defined yet.</td>
          </tr>
          <tr v-for="rule in rules" :key="rule.id">
            <td>
              <div class="rule-name">{{ rule.name }}</div>
              <div class="rule-condition">{{ formatCondition(rule) }}</div>
            </td>
            <td>
              <span class="follow-rate">100%</span> <!-- Placeholder -->
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
  }
});

defineEmits(['edit-rules']);

function formatCondition(rule) {
  if (!rule.condition_type) return '-';
  switch (rule.condition_type) {
    case 'TIME':
      return rule.condition_value.time;
    case 'PERCENTAGE':
      return `${rule.condition_value.percentage}%`;
    case 'FIXED_AMOUNT':
      return `$${rule.condition_value.amount / 1000}k`; // Assuming amount is in dollars
    default:
      return '-';
  }
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

.rule-condition {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.follow-rate {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-feedback-positive-text);
}

.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-base);
}
</style>