<template>
  <div class="daily-checklist">
    <h2 class="view-title">Daily Checklist, {{ formattedDate }}</h2>

    <div v-if="manualRules.length > 0" class="rules-section">
      <h3 class="section-title">MANUAL RULES ({{ manualRules.length }})</h3>
      <ul class="rules-list">
        <li v-for="rule in manualRules" :key="rule.id" class="rule-item">
          <span @click="toggleStatus(rule)" class="status-icon manual-rule">
            <CheckCircleIcon v-if="rule.status === 'completed'" class="icon-completed" />
            <XCircleIconOutline v-else class="icon-pending" />
          </span>
          <span class="rule-label">{{ rule.name }}</span>
        </li>
      </ul>
    </div>

    <div v-if="automatedRules.length > 0" class="rules-section">
      <h3 class="section-title">AUTOMATED RULES ({{ automatedRules.length }})</h3>
      <ul class="rules-list">
        <li v-for="rule in automatedRules" :key="rule.name" class="rule-item">
          <span class="status-icon">
            <CheckCircleIcon v-if="rule.status === 'completed'" class="icon-completed" />
            <XCircleIconSolid v-if="rule.status === 'failed'" class="icon-failed" />
            <XCircleIconOutline v-if="rule.status === 'pending'" class="icon-pending" />
          </span>
          <span class="rule-label">{{ rule.name }}</span>
          <span v-if="rule.progress" class="progress-text">{{ rule.progress }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { CheckCircleIcon, XCircleIcon as XCircleIconSolid } from '@heroicons/vue/24/solid';
import { XCircleIcon as XCircleIconOutline } from '@heroicons/vue/24/outline';

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
  align-self: flex-start;
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
}

.rule-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs); /* Adjusted gap for alignment */
  padding: var(--semantic-size-inset-xs) 0; /* Reduced padding */
}

.rule-label {
    font: var(--semantic-font-style-body-base);
    color: var(--semantic-color-text-primary);
    flex-grow: 1;
}

.progress-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-left: auto;
  padding-left: var(--semantic-size-stack-md);
}

.status-icon {
  flex-shrink: 0;
  width: 24px; /* Standard icon size */
  height: 24px; /* Standard icon size */
  display: flex;
  align-items: center;
  justify-content: center;
}

.manual-rule {
  cursor: pointer;
}

.icon-completed {
  color: var(--semantic-color-text-success);
}

.icon-failed {
  color: var(--semantic-color-text-danger);
}

.icon-pending {
  color: var(--semantic-color-text-disabled);
}
</style>
