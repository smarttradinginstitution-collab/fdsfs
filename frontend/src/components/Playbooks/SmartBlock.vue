
<script setup>
import { ref, watch, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import { useRoute } from 'vue-router';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';
import Draggable from 'vuedraggable';

const props = defineProps({
  block: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['delete-block']);

const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();
const playbookId = computed(() => route.params.id);

const localBlock = ref(JSON.parse(JSON.stringify(props.block)));

const isConditionModalVisible = ref(false);
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

const saveBlock = async () => {
  uiStore.showLoader();
  try {
    await playbookStore.updateBlock(playbookId.value, localBlock.value.id, {
        title: localBlock.value.title,
        content: localBlock.value.content,
    });
  } catch (error) {
    console.error('Failed to save block:', error);
  } finally {
    uiStore.hideLoader();
  }
};

const addGroup = () => {
  const newGroupName = prompt("Enter the name for the new group:", "e.g., Exit Rules");
  if (newGroupName) {
    if (!localBlock.value.content.groups) {
      localBlock.value.content.groups = [];
    }
    localBlock.value.content.groups.push({
      id: `group-${Date.now()}`,
      name: newGroupName,
      items: [],
    });
    saveBlock();
  }
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
    saveBlock();
};

const addChecklist = (group) => {
  const text = prompt("Enter the checklist rule:", "e.g., Price is above 20-SMA");
  if (text) {
    group.items.push({
      id: `item-${Date.now()}`,
      type: 'CHECKLIST',
      data: { text },
    });
    saveBlock();
  }
};

const removeItem = (group, itemId) => {
  group.items = group.items.filter(item => item.id !== itemId);
  saveBlock();
};

const deleteThisBlock = () => {
    if (confirm(`Are you sure you want to delete the block "${props.block.title}"?`)) {
        emit('delete-block', props.block.id);
    }
}
</script>

<template>
  <div class="smart-block">
    <div class="block-header">
      <BaseInput v-model="localBlock.title" @blur="saveBlock" class="block-title-input" />
      <IconButton @click="deleteThisBlock" ariaLabel="Delete Block">
        <TrashIcon />
      </IconButton>
    </div>

    <div class="block-content">
      <Draggable
        v-model="localBlock.content.groups"
        group="groups"
        item-key="id"
        handle=".group-handle"
        @end="saveBlock"
      >
        <template #item="{ element: group }">
          <div class="condition-group">
            <div class="group-header">
              <span class="group-handle">⠿</span>
              <BaseInput v-model="group.name" @blur="saveBlock" class="group-title-input" />
            </div>

            <Draggable
              v-model="group.items"
              group="items"
              item-key="id"
              class="items-list"
              @end="saveBlock"
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
                        <BaseInput v-model="item.data.text" @blur="saveBlock" class="checklist-input" />
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
              <BaseButton @click="addChecklist(group)" variant="secondary">+ Checklist</BaseButton>
            </div>
          </div>
        </template>
      </Draggable>

      <BaseButton @click="addGroup" variant="primary" class="add-group-button">+ Add Group</BaseButton>
    </div>

    <!-- Condition Modal -->
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
/* Main Block Styles */
.smart-block {
    background-color: var(--semantic-color-surface-primary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    margin-bottom: var(--semantic-size-stack-lg);
}
.block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
    background-color: var(--semantic-color-surface-subtle);
    border-bottom: 1px solid var(--semantic-color-border-default);
}
.block-title-input {
    font: var(--semantic-font-style-headline-sm);
    border: none;
    background: transparent;
    padding: 0;
}
.block-content {
    padding: var(--semantic-size-inset-md);
}

/* Group Styles */
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

/* Item Styles */
.items-list {
    min-height: 20px; /* Drop zone for draggable */
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
.condition-text {
  display: flex; align-items: center; gap: var(--semantic-size-inline-sm); flex-grow: 1; font-family: monospace;
}
.checklist-text {
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

/* Modal Styles */
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
