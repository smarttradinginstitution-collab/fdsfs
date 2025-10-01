<template>
  <div class="rule-group-container">
    <!-- Group Header -->
    <div class="group-header">
      <span class="drag-handle drag-handle-group">&#x2832;</span>
      <div v-if="!isEditing" class="title-container">
        <h3 class="group-title">{{ group.name_group }}</h3>
        <ActionsMenu>
          <div class="menu-item" @click="startEditing">Edit</div>
          <div class="menu-item menu-item-danger" @click="isGroupDeleteModalVisible = true">Delete</div>
        </ActionsMenu>
      </div>
      <div v-else class="edit-container">
        <BaseInput
          ref="inputRef"
          v-model="editedName"
          @keyup.enter="saveEdit"
          @keyup.esc="cancelEditing"
        />
        <BaseButton size="small" @click="saveEdit">Save</BaseButton>
        <BaseButton size="small" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
      </div>
    </div>

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
    <div class="rules-list">
      <draggable
        v-model="localRules"
        item-key="id"
        handle=".drag-handle-rule"
        @end="onRuleDragEnd"
      >
        <template #item="{ element: rule }">
          <RuleRow :rule="rule" @delete="promptDeleteRule" />
        </template>
      </draggable>
      <RuleCreator v-if="store.creatingRuleInGroupId === group.id" :group-id="group.id" />
    </div>

    <!-- Footer -->
    <footer class="group-footer">
      <button class="create-rule-btn" @click="store.setCreatingRuleInGroup(group.id)">+ Create new rule</button>
    </footer>
  </div>
</template>

<script setup>
import { defineProps, ref, watch, nextTick } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import RuleRow from './RuleRow.vue';
import draggable from 'vuedraggable';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import RuleCreator from './RuleCreator.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';

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

// --- Inline editing for group title ---
const isEditing = ref(false);
const editedName = ref(props.group.name_group);
const inputRef = ref(null);

const startEditing = async () => {
  editedName.value = props.group.name_group;
  isEditing.value = true;
  await nextTick();
  inputRef.value?.focus();
};

const cancelEditing = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  if (!editedName.value.trim() || editedName.value.trim() === props.group.name_group) {
    cancelEditing();
    return;
  }
  await store.updateRuleGroup({
    playbookId: props.group.playbook_id,
    groupId: props.group.id,
    name_group: editedName.value,
  });
  isEditing.value = false; // The store action will trigger a refresh
};

// --- Delete confirmation for Group ---
const isGroupDeleteModalVisible = ref(false);
const handleConfirmDeleteGroup = () => {
  // Step 1: Just close the modal. The actual deletion is handled by the `onGroupModalClosed` event handler.
  isGroupDeleteModalVisible.value = false;
};
const onGroupModalClosed = async () => {
  // Step 2: Modal has finished its closing animation. Now it's safe to delete and refetch.
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
  // Step 1: Close the modal.
  isRuleDeleteModalVisible.value = false;
};

const onRuleModalClosed = async () => {
  // Step 2: Modal is closed. Now delete the rule.
  if (!ruleToDelete.value) return;
  await store.deleteRule({
    playbookId: props.group.playbook_id,
    ruleId: ruleToDelete.value.id,
  });
  ruleToDelete.value = null; // Clean up
};
</script>

<style scoped>
.rule-group-container {
  padding: var(--semantic-size-inset-md); /* Reduced padding for a more compact feel */
  /* The border is now on the rules list itself, so the bottom border here is removed. */
}

.group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: var(--semantic-size-stack-sm); /* Reduced margin */
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
  padding: 0 0.5rem; /* Make it easier to grab */
  display: flex;
  align-items: center;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-grow: 1;
}

.group-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
}

.edit-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-grow: 1;
}

.rules-list {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  overflow: hidden; /* Ensures the border radius is applied to child elements */
  padding: 0 var(--semantic-size-inset-lg); /* Horizontal padding for the content inside */
}

.group-footer {
  margin-top: var(--semantic-size-stack-xs); /* Extra reduced margin */
}

.create-rule-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-body-md); /* Reduced font size */
  padding: 0.25rem;
  margin-left: 3rem; /* Align with rule text */
}

.create-rule-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>