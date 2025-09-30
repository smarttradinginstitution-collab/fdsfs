<template>
  <div class="playbook-rules-tab">
    <div v-if="store.isRuleGroupsLoading" class="loading-state">
      <p>Loading rules...</p>
    </div>
    <div v-else-if="store.ruleGroupsError" class="error-state">
      <p>Error: {{ store.ruleGroupsError }}</p>
    </div>
    <div v-else class="rules-content">
      <draggable
        v-if="localRuleGroups.length > 0"
        v-model="localRuleGroups"
        class="groups-container"
        item-key="id"
        handle=".drag-handle"
        @end="onGroupDragEnd"
      >
        <template #item="{ element: group }">
          <RuleGroup :group="group" />
        </template>
      </draggable>
      <div v-else class="empty-state">
        <p>No rule groups have been created for this playbook yet.</p>
        <p>Click "+ Create Group" to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import RuleGroup from './RuleGroup.vue';
import draggable from 'vuedraggable';

const store = usePlaybookStore();
const route = useRoute();

const playbookId = computed(() => route.params.id);

// Local state for vuedraggable v-model
const localRuleGroups = ref([]);

// Watch for changes from the store and update the local state
watch(() => store.ruleGroups, (newGroups) => {
  localRuleGroups.value = [...newGroups];
}, { immediate: true, deep: true });


const onGroupDragEnd = async () => {
  const groupIds = localRuleGroups.value.map(group => group.id);
  await store.reorderRuleGroups(playbookId.value, groupIds);
};

onMounted(() => {
  if (playbookId.value) {
    store.fetchRuleGroups(playbookId.value);
  }
});
</script>

<style scoped>
.playbook-rules-tab {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.groups-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}
</style>