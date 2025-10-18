<template>
  <div class="daily-checklist">
    <h2>Daily Checklist, {{ formattedDate }}</h2>

    <div v-if="manualRules.length > 0" class="rules-section">
      <h3 class="section-title">MANUAL RULES ({{ manualRules.length }})</h3>
      <ul>
        <li v-for="rule in manualRules" :key="rule.id" class="rule-item">
          <input
            type="checkbox"
            :id="`rule-${rule.id}`"
            :checked="rule.status === 'completed'"
            @change="toggleStatus(rule)"
            class="custom-checkbox"
          />
          <label :for="`rule-${rule.id}`">{{ rule.name }}</label>
        </li>
      </ul>
    </div>

    <div v-if="automatedRules.length > 0" class="rules-section">
      <h3 class="section-title">AUTOMATED RULES ({{ automatedRules.length }})</h3>
      <ul>
        <li v-for="rule in automatedRules" :key="rule.id" class="rule-item">
          <span class="status-icon" :class="`status-${rule.status}`"></span>
          <span>{{ rule.name }}</span>
          <span class="actual-value">{{ rule.actual_value || '' }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  manualRules: {
    type: Array,
    required: true,
    default: () => []
  },
  automatedRules: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['update-rule-status']);

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric'
  });
});

function toggleStatus(rule) {
  const newStatus = rule.status === 'completed' ? 'pending' : 'completed';
  emit('update-rule-status', rule.id, newStatus);
}
</script>

<style scoped>
.daily-checklist {
  flex-grow: 1;
  padding: 0 2rem;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 2rem;
}

.rules-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--semantic-color-text-secondary);
  margin-bottom: 1rem;
}

ul {
  list-style-type: none;
  padding: 0;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  font-size: 1rem;
}

.custom-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.status-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-pending {
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
}

.status-completed {
  background-color: var(--semantic-color-interactive-success-default);
}

.status-failed {
  background-color: var(--semantic-color-interactive-danger-default);
}

.actual-value {
  margin-left: auto;
  font-size: 0.9rem;
  color: var(--semantic-color-text-secondary);
}
</style>