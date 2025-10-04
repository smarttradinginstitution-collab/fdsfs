<template>
  <div class="folder-list-container">
    <div class="header">
      <h2 class="title">Notebook</h2>
    </div>
    <div class="search-and-new">
      <BaseButton
        :icon="PlusIcon"
        icon-position="left"
        @click="isCreating = true"
      >
        Add folder
      </BaseButton>
      <BaseInput
        v-model="searchTerm"
        placeholder="Search notes..."
        :icon="FilterIcon"
        icon-position="left"
        class="search-input"
      />
    </div>

    <div v-if="isCreating" class="create-folder-form">
      <input
        v-model="newFolderName"
        @keyup.enter="handleCreateFolder"
        @keyup.esc="isCreating = false"
        placeholder="New folder name..."
        class="input-new-folder"
        ref="createInput"
      />
      <button @click="handleCreateFolder" class="button-save">Save</button>
      <button @click="isCreating = false" class="button-cancel">Cancel</button>
    </div>

    <div class="folders-section">
        <div class="section-header">
            <BookOpenIcon class="icon" />
            <h3 class="section-title">Folders</h3>
        </div>
        <div v-if="store.isLoadingFolders" class="loading-spinner">Loading...</div>
        <div v-else-if="store.error" class="error-message">{{ store.error }}</div>
        <ul v-else class="folders">
        <li
            v-for="folder in filteredFolders"
            :key="folder.id"
            @click="selectFolder(folder.id)"
            class="folder-item"
            :class="{ 'is-selected': store.selectedFolderId === folder.id }"
        >
            <span>{{ folder.name }}</span>
            <button @click.stop="handleDeleteFolder(folder.id)" class="delete-button">🗑️</button>
        </li>
        </ul>
    </div>

    <div class="tags-section">
        <div class="section-header">
            <PencilIcon class="icon" />
            <h3 class="section-title">Tags</h3>
        </div>
        <!-- Tags list will be implemented here -->
        <div class="empty-state">
            <p>No tags yet.</p>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseButton from '../ui/BaseButton.vue';
import BaseInput from '../ui/BaseInput.vue';
import PlusIcon from '../icons/PlusIcon.vue';
import FilterIcon from '../icons/FilterIcon.vue';
import BookOpenIcon from '../icons/BookOpenIcon.vue';
import PencilIcon from '../icons/PencilIcon.vue';


const store = useNotebookStore();

const searchTerm = ref('');
const isCreating = ref(false);
const newFolderName = ref('');
const createInput = ref(null);

const filteredFolders = computed(() => {
  if (!searchTerm.value) {
    return store.folders;
  }
  return store.folders.filter(folder =>
    folder.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

watch(isCreating, (val) => {
  if (val) {
    nextTick(() => {
      createInput.value?.focus();
    });
  }
});

const handleCreateFolder = async () => {
  if (!newFolderName.value.trim()) return;
  try {
    await store.createFolder({ name: newFolderName.value });
    newFolderName.value = '';
    isCreating.value = false;
  } catch (error) {
    // Error is handled in the store, maybe show a toast here in the future
    console.error("Failed to create folder:", error);
  }
};

const handleDeleteFolder = async (folderId) => {
    if (confirm('Are you sure you want to delete this folder and all its notes?')) {
        try {
            await store.deleteFolder(folderId);
        } catch (error) {
            console.error("Failed to delete folder:", error);
        }
    }
};

const selectFolder = (folderId) => {
  store.selectFolder(folderId);
};

</script>

<style lang="scss" scoped>
/* Basic styling, will be improved with semantic tokens later */
.folder-list-container {
  padding: 1rem;
  background-color: var(--base-color-gray-800);
  border-right: 1px solid var(--semantic-color-border-default);
  height: 100%;
}

.header {
  margin-bottom: 1rem;
}

.title {
    font-size: 1.25rem;
    font-weight: 600;
    color: white;
}

.search-and-new {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 1rem;
}

.search-input {
    flex-grow: 1;
}

.folders-section, .tags-section {
    margin-top: 1.5rem;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    color: var(--semantic-color-text-primary);
}

.section-title {
    font-weight: 500;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.section-header .icon {
    width: 1rem;
    height: 1rem;
}

.empty-state {
    text-align: center;
    color: var(--semantic-color-text-secondary);
    font-size: 0.875rem;
    padding: 1rem;
}

.create-folder-form {
  margin-bottom: 1rem;
}

.input-new-folder {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    background-color: var(--semantic-color-surface-secondary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    color: var(--semantic-color-text-primary);
}

.folders {
  list-style: none;
  padding: 0;
}

.folder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.5rem;
  cursor: pointer;
  border-radius: var(--semantic-border-radius-interactive);
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-interactive-primary-default);
    color: white;
  }
}

.delete-button {
    background: none;
    border: none;
    color: var(--semantic-color-text-danger);
    cursor: pointer;
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.2s;
}

.folder-item:hover .delete-button {
    visibility: visible;
    opacity: 1;
}
</style>