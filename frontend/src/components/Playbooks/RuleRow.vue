<template>
  <div class="rule-row" :class="{ 'is-editing': isEditing }">
    <div class="col-rule">
      <span class="drag-handle drag-handle-rule">&#x2630;</span>
      <div v-if="!isEditing" class="rule-text">{{ rule.rule }}</div>
      <BaseInput
        v-else
        ref="inputRef"
        v-model="editedText"
        class="edit-input"
        @keyup.enter="saveEdit"
        @keyup.esc="cancelEditing"
      />
    </div>

    <!-- Metrics and Actions (Normal Mode) -->
    <template v-if="!isEditing">
      <div class="col-metric">{{ formatPercentage(rule.metrics.follow_rate) }}</div>
      <div class="col-metric">{{ formatCurrency(rule.metrics.net_pnl) }}</div>
      <div class="col-metric">{{ formatProfitFactor(rule.metrics.profit_factor) }}</div>
      <div class="col-metric">{{ formatPercentage(rule.metrics.win_rate) }}</div>
      <div class="col-action">
        <ActionsMenu>
          <div class="menu-item" @click="startEditing">Edit</div>
          <div class="menu-item menu-item-danger">Delete</div>
        </ActionsMenu>
      </div>
    </template>

    <!-- Save/Cancel Actions (Editing Mode) -->
    <template v-else>
      <div class="edit-actions-container">
        <BaseButton size="sm" @click="saveEdit" :disabled="!editedText.trim()">Save</BaseButton>
        <BaseButton size="sm" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
      </div>
    </template>
  </div>
  <ConfirmationModal
    :show="isDeleteModalVisible"
    title="Delete Rule"
    :message="`Are you sure you want to delete this rule? This action cannot be undone.`"
    @close="isDeleteModalVisible = false"
    @confirm="confirmDeleteRule"
  />
</template>

<script setup>
import { defineProps, ref, nextTick } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useRoute } from 'vue-router';
import { formatCurrency, formatPercentage, formatNumber } from '@/services/formatters.js';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
});

const store = usePlaybookStore();
const route = useRoute();

const formatProfitFactor = (value) => {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return formatNumber(value, 2);
};

// --- Inline editing for rule text ---
const isEditing = ref(false);
const editedText = ref(props.rule.rule);
const inputRef = ref(null);

const startEditing = async () => {
  editedText.value = props.rule.rule;
  isEditing.value = true;
  await nextTick();
  inputRef.value?.focus();
};

const cancelEditing = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  if (!editedText.value.trim() || editedText.value.trim() === props.rule.rule) {
    cancelEditing();
    return;
  }
  await store.updateRule({
    playbookId: route.params.id,
    ruleId: props.rule.id,
    rule: editedText.value,
  });
  isEditing.value = false;
};

// --- Delete confirmation ---
const isDeleteModalVisible = ref(false);

const confirmDeleteRule = async () => {
  await store.deleteRule({
    playbookId: route.params.id,
    ruleId: props.rule.id,
  });
  isDeleteModalVisible.value = false;
};
</script>

<style scoped>
.rule-row {
  display: grid;
  grid-template-columns: minmax(0, 3fr) repeat(4, minmax(0, 1fr)) 40px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
  font: var(--semantic-font-style-body-lg);
}

.rule-row:last-child {
  border-bottom: none;
}

.col-rule {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--semantic-color-text-primary);
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
}

.col-metric {
  text-align: right;
  color: var(--semantic-color-text-primary);
}

.col-action {
  text-align: center;
}

.kebab-menu {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  color: var(--semantic-color-text-secondary);
}

/* --- Edit Mode Styles --- */
.rule-row.is-editing {
  background-color: var(--semantic-color-surface-hover);
}

.edit-input {
  width: 100%;
}

.edit-actions-container {
  grid-column: 2 / -1; /* Span from the second column to the end */
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>