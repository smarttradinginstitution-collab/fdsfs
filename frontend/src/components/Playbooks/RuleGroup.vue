<template>
  <div class="rule-group-card">
    <header class="card-header">
      <div class="header-left">
        <span class="drag-handle drag-handle-group">&#x2630;</span>
        <h3 class="group-title">{{ group.name_group }}</h3>
      </div>
      <div class="header-right">
        <button class="kebab-menu">...</button>
      </div>
    </header>
    <div class="rules-table">
      <div class="table-header">
        <span class="col-rule">Rule</span>
        <span class="col-metric">Follow Rate</span>
        <span class="col-metric">Net Profit / Loss</span>
        <span class="col-metric">Profit Factor</span>
        <span class="col-metric">Win Rate</span>
        <span class="col-action"></span>
      </div>
      <draggable
        v-model="localRules"
        class="table-body"
        item-key="id"
        handle=".drag-handle-rule"
        @end="onRuleDragEnd"
      >
        <template #item="{ element: rule }">
          <RuleRow :rule="rule" />
        </template>
      </draggable>
    </div>
    <footer class="card-footer">
      <button class="create-rule-btn">+ Create new rule</button>
    </footer>
  </div>
</template>

<script setup>
import { defineProps, ref, watch } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import RuleRow from './RuleRow.vue';
import draggable from 'vuedraggable';

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
});

const store = usePlaybookStore();

const localRules = ref([]);

watch(() => props.group.rules, (newRules) => {
  localRules.value = [...newRules];
}, { immediate: true, deep: true });

const onRuleDragEnd = async () => {
  const ruleIds = localRules.value.map(rule => rule.id);
  await store.reorderRules({
    playbookId: props.group.playbook_id, // Pass playbookId for potential error recovery
    groupId: props.group.id,
    rule_ids: ruleIds,
  });
};
</script>

<style scoped>
.rule-group-card {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
}

.group-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
}

.rules-table {
  display: flex;
  flex-direction: column;
}

.table-header {
  display: grid;
  grid-template-columns: minmax(0, 3fr) repeat(4, minmax(0, 1fr)) 40px;
  gap: 1rem;
  padding: 0.75rem var(--semantic-size-inset-md);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.col-metric {
  text-align: right;
}

.card-footer {
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  border-top: 1px solid var(--semantic-color-border-default);
}

.create-rule-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-body-lg);
}

.create-rule-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>