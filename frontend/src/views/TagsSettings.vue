<script setup>
import { onMounted, computed, ref } from 'vue';
import { useTagsStore } from '../stores/tagsStore';
import MainLayout from '../components/layout/MainLayout.vue';
import BaseWidget from '../components/layout/BaseWidget.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import BaseInput from '../components/ui/BaseInput.vue';
import IconButton from '../components/ui/IconButton.vue';
import PencilIcon from '../components/icons/PencilIcon.vue';
import TrashIcon from '../components/icons/TrashIcon.vue';
import ConfirmationModal from '../components/ui/ConfirmationModal.vue';
import ColorSelector from '../components/ui/ColorSelector.vue';

// --- STORE ---
const tagsStore = useTagsStore();

// --- STATE ---
// Group Modal
const isGroupModalOpen = ref(false);
const groupInModal = ref(null);
const newGroupName = ref('');

// Delete Group Modal
const isDeleteConfirmationOpen = ref(false);
const groupToDelete = ref(null);

// Tag Modal
const isTagFormModalOpen = ref(false);
const tagInModal = ref(null);
const newTagName = ref('');
const newTagColor = ref('#4A90E2');
const currentGroupId = ref(null);

// Delete Tag Modal
const isTagDeleteConfirmationOpen = ref(false);
const tagToDelete = ref(null);

// --- COMPUTED ---
const isGroupEditMode = computed(() => !!groupInModal.value);
const isTagEditMode = computed(() => !!tagInModal.value);

// --- METHODS ---
function openAddGroupModal() {
  groupInModal.value = null;
  newGroupName.value = '';
  isGroupModalOpen.value = true;
}

function openEditGroupModal(group) {
  groupInModal.value = group;
  newGroupName.value = group.name_group;
  isGroupModalOpen.value = true;
}

function closeGroupModal() {
  isGroupModalOpen.value = false;
  setTimeout(() => {
    groupInModal.value = null;
    newGroupName.value = '';
  }, 300);
}

async function handleSaveGroup() {
  if (!newGroupName.value.trim()) {
    console.error("Group name cannot be empty.");
    return;
  }
  const groupData = { name_group: newGroupName.value };
  try {
    if (isGroupEditMode.value) {
      await tagsStore.updateTagGroup(groupInModal.value.id, groupData);
    } else {
      await tagsStore.createTagGroup(groupData);
    }
    closeGroupModal();
  } catch (error) {
    console.error("Failed to save the group.", error);
  }
}

function openDeleteConfirmation(group) {
  groupToDelete.value = group;
  isDeleteConfirmationOpen.value = true;
}

async function confirmDeleteGroup() {
  if (!groupToDelete.value) return;
  try {
    await tagsStore.deleteTagGroup(groupToDelete.value.id);
  } catch (error) {
    console.error('Failed to delete group:', error);
  } finally {
    isDeleteConfirmationOpen.value = false;
    groupToDelete.value = null;
  }
}

function openAddTagFormModal(groupId) {
  tagInModal.value = null;
  currentGroupId.value = groupId;
  newTagName.value = '';
  newTagColor.value = '#4A90E2';
  isTagFormModalOpen.value = true;
}

function openEditTagFormModal(tag) {
  tagInModal.value = tag;
  currentGroupId.value = tag.tags_group_id;
  newTagName.value = tag.name_tag;
  newTagColor.value = tag.color;
  isTagFormModalOpen.value = true;
}

function closeTagFormModal() {
  isTagFormModalOpen.value = false;
  setTimeout(() => {
    tagInModal.value = null;
    currentGroupId.value = null;
    newTagName.value = '';
    newTagColor.value = '#4A90E2';
  }, 300);
}

async function handleSaveTag() {
  if (!newTagName.value.trim() || !currentGroupId.value) {
    console.error("Tag name and group ID are required.");
    return;
  }
  const tagData = {
    name_tag: newTagName.value,
    color: newTagColor.value,
    tags_group_id: currentGroupId.value,
  };
  try {
    if (isTagEditMode.value) {
      await tagsStore.updateTag(tagInModal.value.id, tagData);
    } else {
      await tagsStore.createTag(tagData);
    }
    closeTagFormModal();
  } catch (error) {
    console.error("Failed to save the tag.", error);
  }
}

function openTagDeleteConfirmation(tag) {
  tagToDelete.value = tag;
  isTagDeleteConfirmationOpen.value = true;
}

async function confirmTagDelete() {
  if (!tagToDelete.value) return;
  try {
    await tagsStore.deleteTag(tagToDelete.value.id);
  } catch (error) {
    console.error('Failed to delete tag:', error);
  } finally {
    isTagDeleteConfirmationOpen.value = false;
    tagToDelete.value = null;
  }
}

// --- LIFECYCLE HOOKS ---
onMounted(() => {
  tagsStore.fetchTagGroups();
  tagsStore.fetchTags();
});

// --- COMPUTED PROPERTIES ---
const tagGroups = computed(() => tagsStore.tagGroups);
const tags = computed(() => tagsStore.tags);

const getTagsForGroup = (groupId) => {
  return tags.value.filter(tag => tag.tags_group_id === groupId);
};
</script>

<template>
  <MainLayout>
    <div class="tags-settings-page">
      <div class="page-header">
        <div class="header-content">
          <h1>Tags Settings</h1>
          <p class="page-description">Here you can manage your tags and tag groups.</p>
        </div>
        <BaseButton @click="openAddGroupModal">
          Add New Group
        </BaseButton>
      </div>

      <div class="groups-container">
        <BaseWidget
          v-for="group in tagGroups"
          :key="group.id"
          class="tag-group-card"
        >
          <template #title>
            <div class="widget-title">
              <span>{{ group.name_group }}</span>
              <div class="widget-actions">
                <IconButton @click="openEditGroupModal(group)">
                  <PencilIcon />
                </IconButton>
                <IconButton @click="openDeleteConfirmation(group)">
                  <TrashIcon />
                </IconButton>
              </div>
            </div>
          </template>
          <div class="tags-list">
            <div
              v-for="tag in getTagsForGroup(group.id)"
              :key="tag.id"
              class="tag-chip-wrapper"
            >
              <span
                class="tag-chip"
                :style="{ backgroundColor: tag.color || '#cccccc' }"
              >
                {{ tag.name_tag }}
              </span>
              <div class="tag-actions">
                <IconButton class="tag-action-button" @click="openEditTagFormModal(tag)">
                  <PencilIcon />
                </IconButton>
                <IconButton class="tag-action-button" @click="openTagDeleteConfirmation(tag)">
                  <TrashIcon />
                </IconButton>
              </div>
            </div>
            <span v-if="getTagsForGroup(group.id).length === 0" class="no-tags-message">
              No tags in this group yet.
            </span>
            <BaseButton variant="secondary" class="add-tag-button" @click="openAddTagFormModal(group.id)">
              + Add Tag
            </BaseButton>
          </div>
        </BaseWidget>
      </div>
    </div>

    <!-- Add/Edit Group Modal -->
    <BaseModal :show="isGroupModalOpen" @close="closeGroupModal">
      <template #header>
        <h2>{{ isGroupEditMode ? 'Edit Group' : 'Add New Group' }}</h2>
      </template>
      <BaseInput
        v-model="newGroupName"
        label="Group Name"
        placeholder="e.g., Strategies, Market Conditions"
      />
      <template #footer>
        <BaseButton variant="secondary" @click="closeGroupModal">
          Cancel
        </BaseButton>
        <BaseButton @click="handleSaveGroup">
          Save Group
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Add/Edit Tag Modal -->
    <BaseModal :show="isTagFormModalOpen" @close="closeTagFormModal">
      <template #header>
        <h2>{{ isTagEditMode ? 'Edit Tag' : 'Add New Tag' }}</h2>
      </template>
      <div class="form-grid">
        <BaseInput
          v-model="newTagName"
          label="Tag Name"
          placeholder="e.g., Breakout, Reversal"
        />
        <div>
          <label class="color-label">Tag Color</label>
          <ColorSelector v-model="newTagColor" />
        </div>
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="closeTagFormModal">
          Cancel
        </Button>
        <BaseButton @click="handleSaveTag">
          {{ isTagEditMode ? 'Save Changes' : 'Save Tag' }}
        </Button>
      </template>
    </BaseModal>

    <!-- Delete Group Confirmation Modal -->
    <ConfirmationModal
      :show="isDeleteConfirmationOpen"
      title="Delete Group"
      message="Are you sure you want to delete this group? All tags within this group will also be permanently deleted. This action cannot be undone."
      @close="isDeleteConfirmationOpen = false"
      @confirm="confirmDeleteGroup"
    />

    <!-- Delete Tag Confirmation Modal -->
    <ConfirmationModal
      :show="isTagDeleteConfirmationOpen"
      title="Delete Tag"
      :message="`Are you sure you want to permanently delete the tag '${tagToDelete?.name_tag}'? This action cannot be undone.`"
      @close="isTagDeleteConfirmationOpen = false"
      @confirm="confirmTagDelete"
    />
  </MainLayout>
</template>

<style lang="scss" scoped>
.tags-settings-page {
  padding: var(--semantic-size-inset-lg);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-stack-lg);
}
h1 {
  font: var(--semantic-font-style-heading-2xl);
  margin-bottom: var(--semantic-size-stack-xs);
}
.page-description {
  font: var(--semantic-font-style-body-md);
  color: var(--semantic-color-text-secondary);
}
.groups-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--semantic-size-stack-md);
}
.widget-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.widget-actions {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}
.tags-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}
.tag-chip-wrapper {
  position: relative;
  display: inline-flex;
  border-radius: var(--semantic-border-radius-pill);
  overflow: hidden;
}
.tag-chip {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  padding-right: 32px; /* Make space for buttons */
  font: var(--semantic-font-style-label-sm);
  color: var(--base-color-gray-900);
  font-weight: var(--base-font-weight-medium);
  transition: padding 0.2s ease;
}
.tag-actions {
  position: absolute;
  top: 50%;
  right: 4px;
  transform: translateY(-50%);
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.tag-chip-wrapper:hover .tag-actions {
  opacity: 1;
}
.tag-action-button {
  --button-size: 18px;
  width: var(--button-size);
  height: var(--button-size);
  padding: 2px;
  background-color: rgba(0, 0, 0, 0.2);
  color: white;
  border-radius: 50%;
}
.tag-action-button:hover {
  background-color: rgba(0, 0, 0, 0.4);
}
.no-tags-message {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
}
.add-tag-button {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  height: auto;
  font-size: var(--semantic-font-style-label-sm-font-size);
  line-height: var(--semantic-font-style-label-sm-line-height);
  border-style: dashed;
}
.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.color-label {
  display: block;
  font: var(--semantic-font-style-label-md);
  margin-bottom: var(--semantic-size-stack-xs);
}
</style>