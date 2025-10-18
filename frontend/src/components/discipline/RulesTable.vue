<template>
  <div class="rules-table-container">
    <div class="table-header">
      <h3>Current Rules</h3>
      <button @click="$emit('edit-rules')" class="edit-rules-btn">Edit Rules</button>
    </div>
    <table class="rules-table">
      <thead>
        <tr>
          <th>RULE & CONDITION</th>
          <th>FOLLOW RATE</th>
        </tr>
      </thead>
      <tbody>
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
</template>

<script setup>
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
  border-radius: var(--semantic-border-radius-container);
  padding: 1.5rem;
  margin-top: 2rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h3 {
  font-size: 1.2rem;
  font-weight: 600;
}

.edit-rules-btn {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  font-weight: 600;
}

.rules-table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--semantic-color-border-default);
}

th {
  font-size: 0.9rem;
  color: var(--semantic-color-text-secondary);
  font-weight: 700;
}

.rule-name {
  font-weight: 600;
}

.rule-condition {
  font-size: 0.9rem;
  color: var(--semantic-color-text-secondary);
}

.follow-rate {
  font-weight: 600;
  color: var(--semantic-color-text-success);
}
</style>