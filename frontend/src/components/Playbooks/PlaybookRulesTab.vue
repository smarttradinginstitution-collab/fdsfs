<template>
  <div class="playbook-rules-tab">
    <div v-if="store.isRuleGroupsLoading" class="loading-state">
      <p>Loading rules...</p>
    </div>
    <div v-else-if="store.ruleGroupsError" class="error-state">
      <p>Error: {{ store.ruleGroupsError }}</p>
    </div>
    <div v-else class="rules-content">
      <RuleGroupCreator v-if="store.isCreatingGroup" />
      <div class="rules-table-container">
        <!-- Global Table Header -->
        <div class="table-header">
          <span class="col-rule-header"></span> <!-- Empty space for drag handle column -->
          <span class="col-main-header">Rule</span>
          <span class="col-metric">Follow Rate</span>
          <span class="col-metric">Net P/L</span>
          <span class="col-metric">Profit Factor</span>
          <span class="col-metric">Win Rate</span>
          <span class="col-action"></span>
        </div>

        <!-- Groups and Rules -->
        <draggable
          v-if="localRuleGroups.length > 0"
          v-model="localRuleGroups"
          class="groups-container"
          item-key="id"
          handle=".drag-handle-group"
          @end="onGroupDragEnd"
        >
          <template #item="{ element: group }">
            <RuleGroup :group="group" />
          </template>
        </draggable>

        <!-- Empty State -->
        <div v-else class="empty-state-internal">
          <p>No rule groups have been created for this playbook yet.</p>
          <p>Click "+ Create Group" to get started.</p>
        </div>
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
import RuleGroupCreator from './RuleGroupCreator.vue';

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

.rules-table-container {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  overflow: hidden; /* Ensures child borders don't poke out of rounded corners */
}

.table-header {
  display: grid;
  grid-template-columns: 40px 4fr repeat(4, 1.5fr) 60px;
  gap: 1rem;
  padding: 0.75rem var(--semantic-size-inset-lg);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.col-metric {
  text-align: right;
}

/* No gap needed for the new design */
.groups-container {
  display: flex;
  flex-direction: column;
}

.loading-state, .error-state {
  text-align: center;
  padding: 4rem;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}

.empty-state-internal {
  text-align: center;
  padding: 4rem;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}
</style>