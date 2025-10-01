<template>
  <div class="rule-group-section">
    <!-- Group Header Row -->
    <RuleGroupRow :group="group" @delete="isGroupDeleteModalVisible = true" />

    <!-- Modals -->
    <ConfirmationModal
      :show="isGroupDeleteModalVisible"
      title="Delete Rule Group"
      :message="`Are you sure you want to delete the group '${group.name_group}'? This will also delete all rules within it.`"
      @close="isGroupDeleteModalVisible = false"
      @confirm="handleConfirmDeleteGroup"
      @closed="onGroupModalClosed"
    />
    <ConfirmationModal
      :show="isRuleDeleteModalVisible"
      title="Delete Rule"
      message="Are you sure you want to delete this rule? This action cannot be undone."
      @close="isRuleDeleteModalVisible = false"
      @confirm="handleConfirmDeleteRule"
      @closed="onRuleModalClosed"
    />

    <!-- Rules List -->
    <draggable
      v-model="localRules"
      class="rules-list"
      item-key="id"
      handle=".drag-handle-rule"
      @end="onRuleDragEnd"
    >
      <template #item="{ element: rule }">
        <RuleRow :rule="rule" @delete="promptDeleteRule" />
      </template>
    </draggable>

    <!-- Rule Creator -->
    <RuleCreator v-if="store.creatingRuleInGroupId === group.id" :group-id="group.id" />

    <!-- Footer for creating a new rule -->
    <div class="group-footer">
      <button class="create-rule-btn" @click="store.setCreatingRuleInGroup(group.id)">+ Create new rule</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, watch } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import RuleRow from './RuleRow.vue';
import draggable from 'vuedraggable';
import RuleCreator from './RuleCreator.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import RuleGroupRow from './RuleGroupRow.vue'; // New component

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
});

const store = usePlaybookStore();

// --- Drag-and-drop for rules ---
const localRules = ref([]);
watch(() => props.group.rules, (newRules) => {
  localRules.value = [...newRules];
}, { immediate: true, deep: true });

const onRuleDragEnd = async () => {
  const ruleIds = localRules.value.map(rule => rule.id);
  await store.reorderRules({
    playbookId: props.group.playbook_id,
    groupId: props.group.id,
    rule_ids: ruleIds,
  });
};

// --- Delete confirmation for Group ---
const isGroupDeleteModalVisible = ref(false);
const handleConfirmDeleteGroup = () => {
  isGroupDeleteModalVisible.value = false;
};
const onGroupModalClosed = async () => {
  await store.deleteRuleGroup({
    playbookId: props.group.playbook_id,
    groupId: props.group.id,
  });
};

// --- Delete confirmation for Rule ---
const isRuleDeleteModalVisible = ref(false);
const ruleToDelete = ref(null);

const promptDeleteRule = (rule) => {
  ruleToDelete.value = rule;
  isRuleDeleteModalVisible.value = true;
};

const handleConfirmDeleteRule = () => {
  isRuleDeleteModalVisible.value = false;
};

const onRuleModalClosed = async () => {
  if (!ruleToDelete.value) return;
  await store.deleteRule({
    playbookId: props.group.playbook_id,
    ruleId: ruleToDelete.value.id,
  });
  ruleToDelete.value = null;
};
</script>

<style scoped>
/* The main container for a group and its rules */
.rule-group-section {
  /* No border/background here, as it's part of the parent table now */
}

/* The list of rules doesn't need special styling, rows have their own */
.rules-list {
  /* This class is for the draggable component */
}

.group-footer {
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

/* The last group should not have a bottom border on its footer */
.rule-group-section:last-of-type .group-footer {
  border-bottom: none;
}

.create-rule-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-body-lg);
  padding: 0.25rem 0.75rem; /* Make it easier to click */
  margin-left: 2.2rem; /* Align with rule text, past the drag handle */
}

.create-rule-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>