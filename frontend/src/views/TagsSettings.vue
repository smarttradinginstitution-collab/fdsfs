<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Tags Settings</h1>
        <p class="page-subtitle">Manage your tags and tag groups here.</p>
      </div>
      <BaseButton @click="openGroupModal()">
        <PlusIcon class="w-4 h-4 mr-2" />
        Add Group
      </BaseButton>
    </div>

    <!-- LOADING/ERROR STATES -->
    <div v-if="isLoading" class="loading-state"><LoadingSpinner /></div>
    <div v-else-if="error" class="error-state"><p>Error loading tags: {{ error }}</p></div>

    <!-- CONTENT GRID -->
    <div v-else class="content-grid">
      <BaseWidget v-for="group in groupedTags" :key="group.id" class="tag-group-card">
        <template #header>
          <h2 class="group-title">{{ group.name }}</h2>
          <ActionsMenu :items="getGroupActions(group)" />
        </template>

        <div class="tags-container">
          <div v-for="tag in group.tags" :key="tag.id" class="tag-wrapper">
            <BasePill :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }" class="tag-pill">
              {{ tag.name }}
            </BasePill>
            <ActionsMenu :items="getTagActions(tag, group)" class="tag-actions" />
          </div>
          <button @click="openTagModal(group)" class="add-tag-button">
            <PlusIcon class="w-4 h-4" />
          </button>
        </div>
      </BaseWidget>
    </div>
  </div>

  <!-- MODALS -->
  <GroupEditorModal
    :show="isGroupModalOpen"
    :group="editingItem"
    :is-saving="isSaving"
    @close="closeModal"
    @save="handleSaveGroup"
  />
  <TagEditorModal
    :show="isTagModalOpen"
    :tag="editingItem"
    :group-id="currentGroupId"
    :is-saving="isSaving"
    @close="closeModal"
    @save="handleSaveTag"
  />
  <ConfirmationModal
    :show="isConfirmOpen"
    :title="`Delete ${itemToDelete?.type}`"
    :message="`Are you sure you want to delete this ${itemToDelete?.type}? This action cannot be undone.`"
    @close="closeModal"
    @confirm="handleConfirmDelete"
  />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useTagsStore } from '@/stores/tagsStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import BasePill from '@/components/ui/BasePill.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import GroupEditorModal from '@/components/tags/GroupEditorModal.vue';
import TagEditorModal from '@/components/tags/TagEditorModal.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const tagsStore = useTagsStore();
const { groupedTags, isLoading, error, isSaving } = storeToRefs(tagsStore);

// Unified Modal State
const isGroupModalOpen = ref(false);
const isTagModalOpen = ref(false);
const isConfirmOpen = ref(false);
const editingItem = ref(null);
const itemToDelete = ref(null); // { id, type: 'group' | 'tag' }
const currentGroupId = ref(null); // To pass to TagEditorModal

onMounted(() => {
  tagsStore.fetchAllTagsData();
});

// --- Modal Management ---
const closeModal = () => {
  isGroupModalOpen.value = false;
  isTagModalOpen.value = false;
  isConfirmOpen.value = false;
  editingItem.value = null;
  itemToDelete.value = null;
  currentGroupId.value = null;
};

// --- Group Actions ---
const getGroupActions = (group) => [
  { label: 'Edit', action: () => openGroupModal(group) },
  { label: 'Delete', action: () => openConfirmModal(group.id, 'group'), danger: true },
];

const openGroupModal = (group = null) => {
  editingItem.value = group;
  isGroupModalOpen.value = true;
};

const handleSaveGroup = async (groupData) => {
  try {
    if (editingItem.value) {
      await tagsStore.updateTagGroup(groupData.id, groupData);
    } else {
      await tagsStore.createTagGroup(groupData);
    }
    closeModal();
  } catch (e) {
    console.error("Failed to save group:", e);
  }
};

// --- Tag Actions ---
const getTagActions = (tag, group) => [
  { label: 'Edit', action: () => openTagModal(group, tag) },
  { label: 'Delete', action: () => openConfirmModal(tag.id, 'tag'), danger: true },
];

const openTagModal = (group, tag = null) => {
  editingItem.value = tag;
  currentGroupId.value = group.id;
  isTagModalOpen.value = true;
};

const handleSaveTag = async (tagData) => {
  try {
    if (editingItem.value) {
      await tagsStore.updateTag(tagData.id, tagData);
    } else {
      await tagsStore.createTag(tagData);
    }
    closeModal();
  } catch (e) {
    console.error("Failed to save tag:", e);
  }
};

// --- Generic Deletion ---
const openConfirmModal = (id, type) => {
  itemToDelete.value = { id, type };
  isConfirmOpen.value = true;
};

const handleConfirmDelete = async () => {
  if (!itemToDelete.value) return;
  const { id, type } = itemToDelete.value;
  if (type === 'group') {
    await tagsStore.deleteTagGroup(id);
  } else if (type === 'tag') {
    await tagsStore.deleteTag(id);
  }
  closeModal();
};

// --- Utils ---
const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};
</script>

<style scoped>
.page-container { padding: var(--semantic-size-inset-lg); }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--semantic-size-spacing-lg); }
.page-title { font: var(--semantic-font-style-heading-2); color: var(--semantic-color-text-primary); }
.page-subtitle { font: var(--semantic-font-style-body-md); color: var(--semantic-color-text-secondary); margin-top: var(--base-size-spacing-1); }
.loading-state, .error-state { display: flex; justify-content: center; align-items: center; height: 300px; font: var(--semantic-font-style-body-lg); color: var(--semantic-color-text-secondary); }
.content-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: var(--semantic-size-spacing-lg); }
.tag-group-card .group-title { font: var(--semantic-font-style-heading-4); color: var(--semantic-color-text-primary); flex-grow: 1; }
.tags-container { display: flex; flex-wrap: wrap; align-items: center; gap: var(--base-size-spacing-2); padding-top: var(--semantic-size-inset-lg); }

.tag-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.tag-pill {
  font-weight: 600;
  padding-right: 28px; /* Make space for the menu button */
}

.tag-actions {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  --button-bg-color: rgba(255, 255, 255, 0.2);
  --button-text-color: white;
}

.add-tag-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px dashed var(--semantic-color-border-default);
  color: var(--semantic-color-text-secondary);
  background-color: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}
.add-tag-button:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
  border-style: solid;
}
</style>