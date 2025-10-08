<script setup>
import { onMounted, ref } from "vue";
import { useTagsStore } from "@/stores/tagsStore";
import TagGroupCard from "@/components/tags/TagGroupCard.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import CreateOrEditGroupModal from "@/components/tags/CreateOrEditGroupModal.vue";
import CreateOrEditTagModal from "@/components/tags/CreateOrEditTagModal.vue";
import ConfirmationModal from "@/components/ui/ConfirmationModal.vue";

const tagsStore = useTagsStore();

// Modal states
const isGroupModalOpen = ref(false);
const isTagModalOpen = ref(false);

// Data for editing
const editingGroup = ref(null);
const editingTag = ref(null);
const activeGroupIdForTag = ref(null); // To know which group to add/edit a tag in

// Data for deleting
const isConfirmModalOpen = ref(false);
const itemToDelete = ref(null);
const deleteType = ref(''); // 'group' or 'tag'

onMounted(() => {
  // Fetch only if data is not already present
  if (tagsStore.tagsGroups.length === 0 || tagsStore.tags.length === 0) {
    tagsStore.fetchAll();
  }
});

const openAddGroupModal = () => {
  editingGroup.value = null; // Ensure we are not in edit mode
  isGroupModalOpen.value = true;
};

const openEditGroupModal = (group) => {
  editingGroup.value = group;
  isGroupModalOpen.value = true;
};

const openEditTagModal = (tag) => {
  editingTag.value = tag;
  activeGroupIdForTag.value = tag.tags_group_id; // Set the group context
  isTagModalOpen.value = true;
};

const requestDeleteGroup = (group) => {
  itemToDelete.value = group;
  deleteType.value = 'group';
  isConfirmModalOpen.value = true;
};

const requestDeleteTag = (tag) => {
  itemToDelete.value = tag;
  deleteType.value = 'tag';
  isConfirmModalOpen.value = true;
};

const handleConfirmDelete = async () => {
  if (!itemToDelete.value) return;

  if (deleteType.value === 'group') {
    await tagsStore.deleteTagGroup(itemToDelete.value.id);
  } else if (deleteType.value === 'tag') {
    await tagsStore.deleteTag(itemToDelete.value.id);
  }

  // Reset and close modal
  isConfirmModalOpen.value = false;
  itemToDelete.value = null;
  deleteType.value = '';
};
</script>

<template>
  <div class="tags-settings-view">
    <header class="view-header">
      <div class="header-content">
        <h1>Tags Settings</h1>
        <p>Organize and manage your tags and groups.</p>
      </div>
      <BaseButton @click="openAddGroupModal" variant="primary">
        Add New Group
      </BaseButton>
    </header>

    <div v-if="tagsStore.isLoading" class="loading-container">
      <LoadingSpinner />
    </div>

    <div v-else-if="tagsStore.error" class="error-container">
      <p>{{ tagsStore.error }}</p>
    </div>

    <div v-else class="groups-grid">
      <TagGroupCard
        v-for="group in tagsStore.tagsGroups"
        :key="group.id"
        :group="group"
        :tags="tagsStore.getTagsByGroupId(group.id)"
        @edit-group="openEditGroupModal"
        @delete-group="requestDeleteGroup"
        @edit-tag="openEditTagModal"
        @delete-tag="requestDeleteTag"
      />
    </div>

    <CreateOrEditGroupModal
      v-if="isGroupModalOpen"
      v-model="isGroupModalOpen"
      :group="editingGroup"
    />

    <CreateOrEditTagModal
      v-if="isTagModalOpen"
      v-model="isTagModalOpen"
      :tag="editingTag"
      :group-id="activeGroupIdForTag"
    />

    <ConfirmationModal
      :show="isConfirmModalOpen"
      title="Confirm Deletion"
      :message="`Are you sure you want to delete this ${deleteType}? This action cannot be undone.`"
      @close="isConfirmModalOpen = false"
      @confirm="handleConfirmDelete"
    />
  </div>
</template>

<style lang="scss" scoped>
.tags-settings-view {
  padding: var(--semantic-size-inset-lg);
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-stack-xl);

  h1 {
    font: var(--semantic-font-style-heading-2xl);
    color: var(--semantic-color-text-primary);
    margin: 0;
  }
  p {
    font: var(--semantic-font-style-body-md);
    color: var(--semantic-color-text-secondary);
    margin-top: 4px;
  }
}

.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
</style>