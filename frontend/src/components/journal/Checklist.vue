<template>
  <div class="checklist">
    <h3>Daily Checklist</h3>
    <ul>
      <li v-for="rule in rules" :key="rule.id">
        <input
          type="checkbox"
          :checked="rule.status === 'completed'"
          :disabled="rule.rule_type === 'AUTOMATED'"
          @change="updateRuleStatus(rule, $event.target.checked)"
        />
        <span>{{ rule.name }}</span>
        <span v-if="rule.rule_type === 'AUTOMATED'">({{ rule.actual_value || 'pending' }})</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useJournalStore } from '../../stores/journalStore';

const props = defineProps({
  rules: {
    type: Array,
    required: true,
  },
});

const journalStore = useJournalStore();

const updateRuleStatus = (rule, isChecked) => {
  const newStatus = isChecked ? 'completed' : 'pending';
  journalStore.updateManualRuleStatus(rule.id, newStatus);
};
</script>

<style scoped>
.checklist {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}
</style>