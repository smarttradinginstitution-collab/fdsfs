<script setup>
import { ref, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import { useRoute } from 'vue-router';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';
import Draggable from 'vuedraggable';
import AddGroupModal from './AddGroupModal.vue';
import AddChecklistModal from './AddChecklistModal.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
  },
  blockId: {
    type: String,
    required: true,
  },
  blockTitle: {
    type: String,
    required: true,
  }
});

const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();
const playbookId = computed(() => route.params.id);

const localContent = ref(JSON.parse(JSON.stringify(props.content)));

const isConditionModalVisible = ref(false);
const isGroupModalVisible = ref(false);
const isChecklistModalVisible = ref(false);
const currentGroupForAdding = ref(null);
const newConditionData = ref({
  variable: '',
  operator: 'EQUALS',
  value: { type: 'VALUE', value: '' },
  category: 'TECHNICAL',
});

const operatorOptions = [
  { value: 'EQUALS', label: '=' },
  { value: 'NOT_EQUALS', label: '!=' },
  { value: 'GREATER_THAN', label: '>' },
  { value: 'LESS_THAN', label: '<' },
];

const categoryOptions = [
    { value: 'TECHNICAL', label: 'Technical' },
    { value: 'FUNDAMENTAL', label: 'Fundamental' },
    { value: 'SENTIMENT', label: 'Sentiment' },
    { value: 'CUSTOM', label: 'Custom' },
];

const saveContent = async () => {
  uiStore.showLoader();
  try {
    await playbookStore.updateBlock(playbookId.value, props.blockId, {
        title: props.blockTitle, // Pass title along
        content: localContent.value,
    });
  } catch (error) {
    console.error('Failed to save block content:', error);
  } finally {
    uiStore.hideLoader();
  }
};

const handleAddGroup = (groupName) => {
  if (!localContent.value.groups) {
    localContent.value.groups = [];
  }
  localContent.value.groups.push({
    id: `group-${Date.now()}`,
    name: groupName,
    items: [],
  });
  saveContent();
  isGroupModalVisible.value = false;
};

const openConditionModal = (group) => {
    currentGroupForAdding.value = group;
    newConditionData.value = { variable: '', operator: 'EQUALS', value: { type: 'VALUE', value: '' }, category: 'TECHNICAL' };
    isConditionModalVisible.value = true;
};

const addCondition = () => {
    if (!currentGroupForAdding.value) return;
    const newItem = {
        id: `item-${Date.now()}`,
        type: 'CONDITION',
        data: { ...newConditionData.value }
    };
    currentGroupForAdding.value.items.push(newItem);
    isConditionModalVisible.value = false;
    saveContent();
};

const openChecklistModal = (group) => {
  currentGroupForAdding.value = group;
  isChecklistModalVisible.value = true;
};

const handleAddChecklist = (checklistText) => {
  if (currentGroupForAdding.value) {
    currentGroupForAdding.value.items.push({
      id: `item-${Date.now()}`,
      type: 'CHECKLIST',
      data: { text: checklistText },
    });
    saveContent();
  }
  isChecklistModalVisible.value = false;
};

const removeItem = (group, itemId) => {
  group.items = group.items.filter(item => item.id !== itemId);
  saveContent();
};
</script>

<template>
  <div class="rules-editor">
    <Draggable
      v-model="localContent.groups"
      group="groups"
      item-key="id"
      handle=".group-handle"
      @end="saveContent"
    >
      <template #item="{ element: group }">
        <div class="condition-group">
          <div class="group-header">
            <span class="group-handle">⠿</span>
            <BaseInput v-model="group.name" @blur="saveContent" class="group-title-input" />
          </div>

          <Draggable
            v-model="group.items"
            group="items"
            item-key="id"
            class="items-list"
            @end="saveContent"
          >
            <template #item="{ element: item }">
              <div class="list-item">
                  <span class="item-handle">⠿</span>
                  <div v-if="item.type === 'CONDITION'" class="condition-text">
                      <span class="category">[{{ item.data.category }}]</span>
                      <span class="variable">{{ item.data.variable }}</span>
                      <span class="operator">{{ item.data.operator }}</span>
                      <span class="value">{{ item.data.value.value }}</span>
                  </div>
                  <div v-if="item.type === 'CHECKLIST'" class="checklist-text">
                      <span>&#9744;</span>
                      <BaseInput v-model="item.data.text" @blur="saveContent" class="checklist-input" />
                  </div>
                  <IconButton @click="removeItem(group, item.id)" ariaLabel="Delete item" class="delete-item-btn">
                      <TrashIcon />
                  </IconButton>
              </div>
            </template>
          </Draggable>

          <div v-if="!group.items || group.items.length === 0" class="no-items-message">
            No rules in this group.
          </div>

          <div class="add-item-buttons">
            <BaseButton @click="openConditionModal(group)" variant="secondary">+ Condition</BaseButton>
            <BaseButton @click="openChecklistModal(group)" variant="secondary">+ Checklist</BaseButton>
          </div>
        </div>
      </template>
    </Draggable>

    <BaseButton @click="isGroupModalVisible = true" variant="primary" class="add-group-button">+ Add Group</BaseButton>

    <AddGroupModal
      v-if="isGroupModalVisible"
      @close="isGroupModalVisible = false"
      @add-group="handleAddGroup"
    />

    <AddChecklistModal
      v-if="isChecklistModalVisible"
      @close="isChecklistModalVisible = false"
      @add-checklist="handleAddChecklist"
    />

    <div v-if="isConditionModalVisible" class="modal-overlay" @click.self="isConditionModalVisible = false">
        <div class="modal-content">
            <h3>Add New Condition</h3>
            <BaseInput v-model="newConditionData.variable" label="Variable" placeholder="e.g., RSI" />
            <BaseSelect v-model="newConditionData.operator" :options="operatorOptions" label="Operator" />
            <BaseInput v-model="newConditionData.value.value" label="Value" placeholder="e.g., 70" />
            <BaseSelect v-model="newConditionData.category" :options="categoryOptions" label="Category" />
            <div class="modal-actions">
                <BaseButton @click="isConditionModalVisible = false" variant="secondary">Cancel</BaseButton>
                <BaseButton @click="addCondition" variant="primary">Add</BaseButton>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles from the original SmartBlock.vue */
.condition-group {
  background-color: var(--semantic-color-surface-subtle);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-md);
  border: 1px solid var(--semantic-color-border-subtle);
}
.group-header {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-inline-sm);
    margin-bottom: var(--semantic-size-stack-md);
}
.group-title-input {
  font: var(--semantic-font-style-body-lg-bold);
  border: none;
  background: transparent;
  padding: 0;
  flex-grow: 1;
}
.items-list {
    min-height: 20px;
}
.list-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inline-sm);
  padding: var(--semantic-size-inset-xs);
  margin-bottom: var(--semantic-size-stack-xs);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-element);
  border: 1px solid var(--semantic-color-border-default);
}
.item-handle, .group-handle {
    cursor: grab;
    color: var(--semantic-color-text-subtle);
    padding: 0 var(--semantic-size-inline-sm);
}
.condition-text, .checklist-text {
  display: flex; align-items: center; gap: var(--semantic-size-inline-sm); flex-grow: 1;
}
.checklist-input {
    border: none; background: transparent; padding: 0; width: 100%;
}
.delete-item-btn { margin-left: auto; }
.add-item-buttons {
  display: flex; gap: var(--semantic-size-inline-md); margin-top: var(--semantic-size-stack-md); border-top: 1px solid var(--semantic-color-border-subtle); padding-top: var(--semantic-size-stack-md);
}
.add-group-button {
  margin-top: var(--semantic-size-stack-md); display: block; margin-left: auto; margin-right: auto;
}
.no-items-message {
    font-style: italic; color: var(--semantic-color-text-subtle); text-align: center; padding: var(--semantic-size-inset-md);
}
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.5); display: flex;
    justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
    background-color: var(--semantic-color-surface-primary);
    padding: var(--semantic-size-inset-lg);
    border-radius: var(--semantic-border-radius-surface);
    min-width: 400px; display: flex; flex-direction: column; gap: var(--semantic-size-stack-md);
}
.modal-actions {
    display: flex; justify-content: flex-end; gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-md);
}
</style>
