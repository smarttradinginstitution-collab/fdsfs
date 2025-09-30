<script setup>
import { ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import draggable from 'vuedraggable';
import BaseButton from '@/components/ui/BaseButton.vue';
import RuleGroupCard from './RuleGroupCard.vue';

const ruleGroups = ref([]);

const addGroup = () => {
  ruleGroups.value.push({
    id: uuidv4(), // Temporary frontend ID for list rendering
    title: 'New Group',
    rules: [],
  });
};

const removeGroup = (groupId) => {
  ruleGroups.value = ruleGroups.value.filter(group => group.id !== groupId);
};

const updateGroup = (updatedGroup) => {
  const index = ruleGroups.value.findIndex(g => g.id === updatedGroup.id);
  if (index !== -1) {
    ruleGroups.value[index] = updatedGroup;
  }
};

// Expose the ruleGroups data to the parent component
defineExpose({
  ruleGroups,
});
</script>

<template>
  <div class="rule-group-manager">
    <div class="manager-header">
      <div class="header-text">
        <h2>Trading Playbook Rules</h2>
        <p>Define your playbook rules with grouping.</p>
      </div>
      <BaseButton @click="addGroup" variant="primary">+ Create New Group</BaseButton>
    </div>

    <draggable
      v-model="ruleGroups"
      item-key="id"
      handle=".drag-handle"
      class="groups-list"
      ghost-class="ghost"
    >
      <template #item="{ element: group }">
        <RuleGroupCard
          :group="group"
          @update:group="updateGroup"
          @delete:group="removeGroup(group.id)"
        />
      </template>
    </draggable>

     <div v-if="ruleGroups.length === 0" class="empty-state">
      <p>No rule groups yet. Click "+ Create New Group" to get started.</p>
    </div>
  </div>
</template>

<style scoped>
.rule-group-manager {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h2 {
  font: var(--semantic-font-style-heading-h2);
  color: var(--semantic-color-text-primary);
  margin: 0 0 var(--semantic-size-stack-xs) 0;
}

.header-text p {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  margin: 0;
}

.groups-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
  border: 1px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
}

.ghost {
  opacity: 0.5;
  background: var(--semantic-color-surface-subtle);
}
</style>