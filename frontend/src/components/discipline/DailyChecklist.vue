<template>
  <div class="daily-checklist">
    <h2 class="view-title">Daily Checklist, {{ formattedDate }}</h2>

    <div v-if="manualRules.length > 0" class="rules-section">
      <h3 class="section-title">MANUAL RULES ({{ manualRules.length }})</h3>
      <ul class="rules-list">
        <li v-for="rule in manualRules" :key="rule.id" class="rule-item">
          <BaseCheckbox
            :id="`rule-${rule.id}`"
            :model-value="rule.status === 'completed'"
            @update:model-value="toggleStatus(rule)"
          >
            <span class="manual-rule-label">{{ rule.name }}</span>
          </BaseCheckbox>
        </li>
      </ul>
    </div>

    <div v-if="automatedRules.length > 0" class="rules-section">
      <h3 class="section-title">AUTOMATED RULES ({{ automatedRules.length }})</h3>
      <ul class="rules-list">
        <AutomatedRuleItem
          v-for="rule in automatedRules"
          :key="rule.id"
          :rule="rule"
        />
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import AutomatedRuleItem from './AutomatedRuleItem.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';

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

/* BaseCheckbox handles its own styling, so custom styles for checkbox and label are no longer needed here. */

.manual-rule-label {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
  /* Ensure the label aligns nicely with the custom checkbox */
  position: relative;
  top: -2px;
}

.status-icon {
  font-size: 1.2em; /* Adjust size of the emoji */
  line-height: 1; /* Ensure proper vertical alignment */
  flex-shrink: 0;
}
</style>