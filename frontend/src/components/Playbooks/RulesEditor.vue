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
import GripVerticalIcon from '@/components/icons/GripVerticalIcon.vue';
import ConditionChip from './ConditionChip.vue';

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
      class="groups-container"
    >
      <template #item="{ element: group }">
        <div class="condition-group group"> <!-- Add 'group' for hover context -->
          <h4 class="group-title">{{ group.name }}</h4>

          <Draggable
            v-model="group.items"
            group="items"
            item-key="id"
            class="items-list"
            @end="saveContent"
          >
            <template #item="{ element: item }">
              <div class="list-item group"> <!-- Add 'group' for hover context -->
                  <GripVerticalIcon class="drag-handle" />

                  <ConditionChip v-if="item.type === 'CONDITION'" :condition="item.data" />

                  <div v-if="item.type === 'CHECKLIST'" class="checklist-text">
                      <div class="checkbox"></div>
                      <input v-model="item.data.text" @blur="saveContent" class="input-ghost checklist-input" placeholder="Write a rule..." />
                  </div>

                  <div class="item-actions">
                     <IconButton @click="removeItem(group, item.id)" ariaLabel="Delete item">
                        <TrashIcon />
                    </IconButton>
                  </div>
              </div>
            </template>
          </Draggable>

          <div class="add-item-buttons">
              <button @click="openConditionModal(group)" class="ghost-button">+ Add Condition</button>
              <button @click="openChecklistModal(group)" class="ghost-button">+ Add Checklist</button>
          </div>
        </div>
      </template>
    </Draggable>

    <button @click="isGroupModalVisible = true" class="dashed-button">+ Add New Group</button>

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
.rules-editor {
    display: flex;
    flex-direction: column;
    gap: 1.5rem; /* 24px */
}
.condition-group {
  padding: 0;
  margin: 0;
}
.group-title {
    font-size: 11px;
    font-weight: 600;
    color: #8A91A0; /* gray-500 */
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem; /* 12px - Increased spacing */
    padding-left: 0.5rem; /* 8px */
}
.items-list {
    display: flex;
    flex-direction: column;
}
.list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem; /* 12px */
  padding: 0.5rem; /* 8px */
  margin: 0 -0.5rem; /* -8px to align hover bg */
  border-radius: 6px;
  transition: background-color 0.2s ease-in-out;
}
.list-item:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
.drag-handle {
    opacity: 0;
    cursor: grab;
    color: #6B7280; /* gray-600 */
    transition: opacity 0.2s ease-in-out;
}
.list-item:hover .drag-handle {
    opacity: 1;
}
.checkbox {
    width: 1rem; /* 16px */
    height: 1rem; /* 16px */
    border: 1px solid #4B5563; /* gray-600 */
    border-radius: 4px;
    flex-shrink: 0;
}
.condition-text, .checklist-text {
  display: flex; align-items: center; gap: 0.75rem; flex-grow: 1;
}
.checklist-input {
    font-size: 14px;
    color: #D1D5DB; /* gray-200 */
    font-weight: 500;
}
.checklist-input::placeholder {
    color: #4B5563; /* gray-600 */
}
.item-actions {
    display: flex;
    gap: 0.5rem; /* 8px */
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}
.list-item:hover .item-actions {
    opacity: 1;
}
.add-item-buttons {
  display: flex;
  gap: 1rem; /* 16px */
  margin-top: 0.5rem; /* 8px */
  padding-left: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}
.condition-group:hover .add-item-buttons {
    opacity: 1;
}
.ghost-button {
    background: none;
    border: none;
    color: var(--semantic-color-text-subtle);
    cursor: pointer;
    padding: var(--semantic-size-inset-xs);
    font-size: 13px;
    transition: color 0.2s;
}
.ghost-button:hover {
    color: var(--semantic-color-text-primary);
}
.dashed-button {
    width: 100%;
    padding: var(--semantic-size-inset-md);
    border: 2px dashed var(--semantic-color-border-subtle);
    border-radius: var(--semantic-border-radius-surface);
    background: transparent;
    color: var(--semantic-color-text-subtle);
    cursor: pointer;
    transition: all 0.2s;
}
.dashed-button:hover {
    border-color: var(--semantic-color-primary-default);
    color: var(--semantic-color-text-primary);
}

/* Modal Styles */
:deep(.modal-overlay) {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6); display: flex;
    justify-content: center; align-items: center; z-index: 1000;
}
:deep(.modal-content) {
    background-color: var(--semantic-color-surface-primary);
    padding: var(--semantic-size-inset-lg);
    border-radius: var(--semantic-border-radius-surface);
    min-width: 400px; display: flex; flex-direction: column; gap: var(--semantic-size-stack-md);
}
:deep(.modal-actions) {
    display: flex; justify-content: flex-end; gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-md);
}
</style>
