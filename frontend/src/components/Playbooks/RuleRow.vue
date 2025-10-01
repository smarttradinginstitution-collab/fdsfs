<template>
  <div class="rule-row" :class="{ 'is-editing': isEditing }">
    <!-- Col 1: Drag Handle -->
    <span class="drag-handle drag-handle-rule">
      <DragHandleIcon />
    </span>

    <!-- Col 2: Rule Text / Input -->
    <div class="col-rule-text">
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
          <div class="menu-item menu-item-danger" @click="emit('delete', rule)">Delete</div>
        </ActionsMenu>
      </div>
    </template>

    <!-- Save/Cancel Actions (Editing Mode) -->
    <div v-if="isEditing" class="edit-actions-container">
      <BaseButton size="sm" @click="saveEdit" :disabled="!editedText.trim()">Save</BaseButton>
      <BaseButton size="sm" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, nextTick, defineEmits } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useRoute } from 'vue-router';
import { formatCurrency, formatPercentage, formatNumber } from '@/services/formatters.js';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import DragHandleIcon from '@/components/icons/DragHandleIcon.vue';

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['delete']);

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
</script>

<style scoped>
.rule-row {
  display: grid;
  grid-template-columns: 40px 4fr repeat(4, 1.5fr) 60px;
  gap: 0.75rem; /* Further reduced gap */
  align-items: center;
  padding: 0.25rem 0; /* Further reduced vertical padding */
  border-bottom: 1px solid var(--semantic-color-border-default);
  font: var(--semantic-font-style-body-sm); /* Further reduced font size */
}

.rule-row:last-child {
  border-bottom: none;
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
  display: flex;
  align-items: center;
  justify-content: center;
}

.col-rule-text {
  color: var(--semantic-color-text-primary);
}

.col-metric {
  text-align: right;
  color: var(--semantic-color-text-primary);
}

.col-action {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* --- Edit Mode Styles --- */
.rule-row.is-editing {
  background-color: var(--semantic-color-surface-hover);
}

.rule-row.is-editing .col-rule-text {
  grid-column: 2 / 3;
}

.edit-input {
  width: 100%;
}

.edit-actions-container {
  grid-column: 3 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>