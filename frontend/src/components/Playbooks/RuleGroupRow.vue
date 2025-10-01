<template>
  <div class="group-row" :class="{ 'is-editing': isEditing }">
    <!-- Col 1: Drag Handle -->
    <span class="drag-handle drag-handle-group">&#x2630;</span>

    <!-- Normal Mode -->
    <template v-if="!isEditing">
      <div class="title-container">
        <h3 class="group-title">{{ group.name_group }}</h3>
      </div>
      <!-- This spacer ensures the actions menu aligns to the last column -->
      <div class="spacer"></div>
      <div class="actions-container">
        <ActionsMenu>
          <div class="menu-item" @click="startEditing">Edit</div>
          <div class="menu-item menu-item-danger" @click="$emit('delete')">Delete</div>
        </ActionsMenu>
      </div>
    </template>

    <!-- Editing Mode -->
    <template v-else>
      <div class="edit-container">
        <BaseInput
          ref="inputRef"
          v-model="editedName"
          @keyup.enter="saveEdit"
          @keyup.esc="cancelEditing"
        />
      </div>
      <div class="edit-actions">
        <BaseButton size="small" @click="saveEdit">Save</BaseButton>
        <BaseButton size="small" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
      </div>
    </template>
  </div>
</template>

<script setup>
import { defineProps, ref, nextTick, defineEmits } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['delete']);

const store = usePlaybookStore();

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
</script>

<style scoped>
.group-row {
  display: grid;
  /* A simpler grid to align with the main table's handle, content, and action columns */
  grid-template-columns: 40px 1fr 60px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem var(--semantic-size-inset-lg);
  background-color: var(--semantic-color-surface-secondary);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.drag-handle {
  cursor: grab;
  color: var(--semantic-color-text-placeholder);
  text-align: center;
}

.group-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
}

.actions-container {
  text-align: center;
}

.edit-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}
</style>