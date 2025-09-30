<script setup>
import { ref, watch } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import draggable from 'vuedraggable';
import RuleItem from './RuleItem.vue';
import DragHandleIcon from '@/components/icons/DragHandleIcon.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:group', 'delete:group']);

const localGroup = ref(JSON.parse(JSON.stringify(props.group)));
const isEditing = ref(false);

watch(localGroup, (newGroup) => {
  emit('update:group', newGroup);
}, { deep: true });

const addRule = () => {
  localGroup.value.rules.push({
    id: uuidv4(), // Temporary frontend ID
    description: '',
  });
};

const removeRule = (ruleId) => {
  localGroup.value.rules = localGroup.value.rules.filter(rule => rule.id !== ruleId);
};

const updateRule = (updatedRule) => {
    const index = localGroup.value.rules.findIndex(r => r.id === updatedRule.id);
    if (index !== -1) {
        localGroup.value.rules[index] = updatedRule;
    }
}
</script>

<template>
  <div class="rule-group-card">
    <div class="card-header">
      <div class="drag-handle">
        <DragHandleIcon />
      </div>
      <div v-if="!isEditing" class="group-title">{{ localGroup.title }}</div>
      <BaseInput v-else v-model="localGroup.title" @blur="isEditing = false" class="title-input"/>
      <div class="header-actions">
        <button @click="isEditing = !isEditing" class="action-btn">{{ isEditing ? 'Save' : 'Edit' }}</button>
        <button @click="$emit('delete:group')" class="action-btn delete">Delete</button>
      </div>
    </div>
    <div class="rules-container">
        <draggable
            v-model="localGroup.rules"
            item-key="id"
            class="rules-list"
            ghost-class="ghost"
        >
            <template #item="{ element: rule }">
                <RuleItem
                    :rule="rule"
                    @update:rule="updateRule"
                    @delete:rule="removeRule(rule.id)"
                />
            </template>
        </draggable>
      <BaseButton variant="secondary" @click="addRule" class="add-rule-btn">+ Create new rule</BaseButton>
    </div>
  </div>
</template>

<style scoped>
.rule-group-card {
  background-color: var(--semantic-color-surface-subtle);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-secondary);
}
.drag-handle:active {
  cursor: grabbing;
}

.group-title {
  font: var(--semantic-font-style-body-xl-bold);
  color: var(--semantic-color-text-primary);
  flex-grow: 1;
}

.title-input {
    flex-grow: 1;
}

.header-actions {
  display: flex;
  gap: var(--semantic-size-stack-sm);
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}
.action-btn:hover {
    color: var(--semantic-color-text-primary);
}
.action-btn.delete {
    color: var(--semantic-color-text-danger);
}
.action-btn.delete:hover {
    color: var(--semantic-color-text-danger-hover);
}

.rules-container {
  padding: var(--semantic-size-inset-md);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.rules-list {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xs);
    margin-bottom: var(--semantic-size-stack-sm);
}

.add-rule-btn {
  align-self: flex-start;
}

.ghost {
  opacity: 0.5;
  background: var(--semantic-color-surface-default);
}
</style>