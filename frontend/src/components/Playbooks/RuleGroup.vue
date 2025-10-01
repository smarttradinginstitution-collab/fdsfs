<template>
  <div class="rule-group-container">
    <!-- Group Header -->
    <div class="group-header">
      <span class="drag-handle drag-handle-group">
        <DragHandleIcon />
      </span>
      <template v-if="!isEditing">
        <h3 class="group-title">{{ group.name_group }}</h3>
        <ActionsMenu class="group-actions">
          <div class="menu-item" @click="startEditing">Edit</div>
          <div class="menu-item menu-item-danger" @click="isGroupDeleteModalVisible = true">Delete</div>
        </ActionsMenu>
      </template>
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
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import RuleCreator from './RuleCreator.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import DragHandleIcon from '@/components/icons/DragHandleIcon.vue';

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
    playbookId: props.group.playbook_id,
    groupId: props.group.id,
    rule_ids: ruleIds,
  });
};

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
  isEditing.value = false;
};

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
.rule-group-container {
  padding: var(--semantic-size-inset-md);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: var(--semantic-size-stack-sm);
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
  padding: 0 0.5rem;
}

.drag-handle :deep(svg) {
  display: block; /* The definitive fix for vertical alignment */
}

.group-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
  flex-grow: 1;
  margin: 0; /* Reset default browser margins */
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
  overflow: hidden;
  padding: 0 var(--semantic-size-inset-lg);
}

.group-footer {
  margin-top: var(--semantic-size-stack-xs);
}

.create-rule-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-body-md);
  padding: 0.25rem;
  margin-left: 3rem;
}

.create-rule-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>