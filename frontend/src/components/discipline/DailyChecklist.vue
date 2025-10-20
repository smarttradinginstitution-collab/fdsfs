<template>
  <div class="daily-checklist">
    <h2 class="view-title">Daily Checklist, {{ formattedDate }}</h2>

    <div v-if="manualRules.length > 0" class="rules-section">
      <h3 class="section-title">MANUAL RULES ({{ manualRules.length }})</h3>
      <ul class="rules-list">
        <li v-for="rule in manualRules" :key="rule.id" class="rule-item">
          <input
            type="checkbox"
            :id="`rule-${rule.id}`"
            :checked="rule.status === 'completed'"
            @change="toggleStatus(rule)"
            class="custom-checkbox"
          />
          <label :for="`rule-${rule.id}`" class="rule-label">{{ rule.name }}</label>
        </li>
      </ul>
    </div>

    <div v-if="automatedRules.length > 0" class="rules-section">
      <h3 class="section-title">AUTOMATED RULES ({{ automatedRules.length }})</h3>
      <ul class="rules-list">
        <li v-for="rule in automatedRules" :key="rule.id" class="rule-item">
          <span class="status-icon">
            <template v-if="rule.status === 'completed'">✅</template>
            <template v-else-if="rule.status === 'failed'">❌</template>
            <template v-else>⚪</template>
          </span>
          <span class="rule-label">{{ rule.name }}</span>
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
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  align-self: flex-start; /* Prevent stretching */
}

.view-title {
  font: var(--semantic-font-style-heading-lg);
  margin-bottom: var(--semantic-size-stack-lg);
}

.rules-section {
  margin-bottom: var(--semantic-size-stack-lg);
}

.section-title {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase;
  margin-bottom: var(--semantic-size-stack-md);
}

.rules-list {
  list-style-type: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.rule-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-sm) 0;
}

.rule-label {
    font: var(--semantic-font-style-body-base);
    color: var(--semantic-color-text-primary);
}

.custom-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--semantic-color-interactive-primary-default);
}

.status-icon {
  font-size: 1.2em; /* Adjust size of the emoji */
  line-height: 1; /* Ensure proper vertical alignment */
  flex-shrink: 0;
}
</style>