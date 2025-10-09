<template>
  <div class="tag-group-container">
    <!-- Group Header -->
    <div class="group-header">
      <span class="drag-handle">
        <DragHandleIcon />
      </span>
      <template v-if="!isEditingGroup">
        <h3 class="group-title">{{ group.name }}</h3>
        <ActionsMenu class="group-actions">
          <template #default="{ closeMenu }">
            <div class="menu-item" @click="() => { startEditingGroup(); closeMenu(); }">Edit</div>
            <div class="menu-item menu-item-danger" @click="() => { isGroupDeleteModalVisible = true; closeMenu(); }">Delete</div>
          </template>
        </ActionsMenu>
      </template>
      <div v-else class="edit-container">
        <BaseInput
          ref="inputRef"
          v-model="editedGroupName"
          @keyup.enter="saveGroupEdit"
          @keyup.esc="cancelGroupEditing"
        />
        <BaseButton size="small" @click="saveGroupEdit" :loading="isSaving">Save</BaseButton>
        <BaseButton size="small" variant="secondary" @click="cancelGroupEditing">Cancel</BaseButton>
      </div>
    </div>

    <!-- Modals for Deletion Confirmation -->
    <ConfirmationModal
      v-if="isGroupDeleteModalVisible"
      :show="isGroupDeleteModalVisible"
      title="Delete Group"
      :message="`Are you sure you want to delete the group '${group.name}'? This will also delete all tags within it.`"
      @close="isGroupDeleteModalVisible = false"
      @confirm="handleConfirmDeleteGroup"
    />
    <ConfirmationModal
      v-if="isTagDeleteModalVisible"
      :show="isTagDeleteModalVisible"
      title="Delete Tag"
      message="Are you sure you want to delete this tag? This action cannot be undone."
      @close="isTagDeleteModalVisible = false"
      @confirm="handleConfirmDeleteTag"
    />

    <!-- Tags List -->
    <div class="tags-list">
      <TagRow
        v-for="tag in group.tags"
        :key="tag.id"
        :tag="tag"
        @delete="promptDeleteTag"
      />
      <TagCreator v-if="store.creatingTagInGroupId === group.id" :group-id="group.id" />
    </div>

    <!-- Footer -->
    <footer class="group-footer">
      <button class="create-tag-btn" @click="store.setCreatingTagInGroup(group.id)">+ Create new tag</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, defineProps, nextTick, computed } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import TagRow from './TagRow.vue';
import TagCreator from './TagCreator.vue';
import DragHandleIcon from '@/components/icons/DragHandleIcon.vue';

const props = defineProps({
  group: { type: Object, required: true },
});

const store = useTagsStore();
const isSaving = computed(() => store.isSaving);

// Group Editing State
const isEditingGroup = ref(false);
const editedGroupName = ref('');
const inputRef = ref(null);

const startEditingGroup = async () => {
  editedGroupName.value = props.group.name;
  isEditingGroup.value = true;
  await nextTick();
  inputRef.value?.focus();
};

const cancelGroupEditing = () => {
  isEditingGroup.value = false;
};

const saveGroupEdit = async () => {
  if (!editedGroupName.value.trim() || editedGroupName.value.trim() === props.group.name) {
    cancelGroupEditing();
    return;
  }
  await store.updateTagGroup(props.group.id, { name: editedGroupName.value });
  isEditingGroup.value = false;
};

// Deletion Modals State
const isGroupDeleteModalVisible = ref(false);
const isTagDeleteModalVisible = ref(false);
const tagToDelete = ref(null);

const handleConfirmDeleteGroup = async () => {
  await store.deleteTagGroup(props.group.id);
  isGroupDeleteModalVisible.value = false;
};

const promptDeleteTag = (tag) => {
  tagToDelete.value = tag;
  isTagDeleteModalVisible.value = true;
};

const handleConfirmDeleteTag = async () => {
  if (!tagToDelete.value) return;
  await store.deleteTag(tagToDelete.value.id);
  isTagDeleteModalVisible.value = false;
  tagToDelete.value = null;
};
</script>

<style scoped>
.tag-group-container {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
}

.group-header {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
  margin-bottom: var(--semantic-size-stack-md);
}

.drag-handle {
  cursor: grab;
  height: 0.8rem;
  color: var(--semantic-color-text-placeholder);
}

.group-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  flex-grow: 1;
}

.edit-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
  flex-grow: 1;
}

.tags-list {
  display: flex;
  flex-direction: column;
}

.group-footer {
  margin-top: var(--semantic-size-stack-sm);
}

.create-tag-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-label-md);
  padding: var(--semantic-size-stack-xxs);
}

.create-tag-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>
