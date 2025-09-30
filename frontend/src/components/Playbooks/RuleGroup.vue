<template>
  <BaseWidget class="rule-group-widget">
    <template #header>
      <div class="widget-header-content">
        <div class="header-left">
          <span class="drag-handle drag-handle-group">&#x2630;</span>
          <div v-if="!isEditing" class="title-container">
            <h3 class="group-title">{{ group.name_group }}</h3>
          </div>
          <div v-else class="edit-container">
            <BaseInput
              ref="inputRef"
              v-model="editedName"
              @keyup.enter="saveEdit"
              @keyup.esc="cancelEditing"
            />
            <BaseButton size="sm" @click="saveEdit">Save</BaseButton>
            <BaseButton size="sm" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
          </div>
        </div>
        <div v-if="!isEditing" class="header-right">
          <ActionsMenu>
            <div class="menu-item" @click="startEditing">Edit</div>
            <div class="menu-item menu-item-danger" @click="isDeleteModalVisible = true">Delete</div>
          </ActionsMenu>
        </div>
      </div>
    </template>

    <div class="widget-body-content">
      <ConfirmationModal
        :show="isDeleteModalVisible"
        title="Delete Rule Group"
        :message="`Are you sure you want to delete the group '${group.name_group}'? This will also delete all rules within it.`"
        @close="isDeleteModalVisible = false"
        @confirm="confirmDeleteGroup"
      />
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
        <RuleCreator v-if="store.creatingRuleInGroupId === group.id" :group-id="group.id" />
      </div>
      <footer class="card-footer">
        <button class="create-rule-btn" @click="store.setCreatingRuleInGroup(group.id)">+ Create new rule</button>
      </footer>
    </div>
  </BaseWidget>
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

// --- Delete confirmation ---
const isDeleteModalVisible = ref(false);

const confirmDeleteGroup = async () => {
  await store.deleteRuleGroup({
    playbookId: props.group.playbook_id,
    groupId: props.group.id,
  });
  isDeleteModalVisible.value = false; // The store action refreshes the list
};
</script>

<style scoped>
.rule-group-widget :deep(.widget-content) {
  padding: 0;
}

.widget-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
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

.edit-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.widget-body-content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.rules-table {
  display: flex;
  flex-direction: column;
}

.table-header {
  display: grid;
  grid-template-columns: minmax(0, 3fr) repeat(4, minmax(0, 1fr)) 40px;
  gap: 1rem;
  padding: 0.75rem var(--semantic-size-inset-lg);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.table-body {
  /* The rows inside will have their own bottom border */
}

.col-metric {
  text-align: right;
}

.card-footer {
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-lg);
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

.kebab-menu {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  color: var(--semantic-color-text-secondary);
}
</style>