<template>
  <div class="simple-label-card">
    <!-- HEADER -->
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
    </div>

    <!-- LOADING / EMPTY STATES -->
    <div v-if="isLoading" class="state-container"><LoadingSpinner /></div>
    <div v-else-if="!items.length && !isCreating" class="state-container empty-state">
      No {{ itemTypeName.toLowerCase() }}s found.
    </div>

    <!-- ITEMS LIST -->
    <div v-else class="items-list">
      <div v-for="item in items" :key="item.id" class="item-row">
        <!-- VIEW MODE -->
        <template v-if="editingItemId !== item.id">
          <div class="item-details">
            <span class="item-color-dot" :style="{ backgroundColor: item.color }"></span>
            <span class="item-name">{{ item.name }}</span>
          </div>
          <div class="item-actions">
            <button @click="startEditing(item)" class="action-btn"><PencilIcon class="icon" /></button>
            <button @click="promptDelete(item)" class="action-btn"><TrashIcon class="icon icon-danger" /></button>
          </div>
        </template>
        <!-- EDIT MODE -->
        <template v-else>
          <div class="edit-container">
            <BaseInput v-model="editedItem.name" ref="editInputRef" placeholder="Item name..." />
            <ColorSelector v-model="editedItem.color" />
            <BaseButton size="small" @click="handleUpdateItem" :loading="isSaving">Save</BaseButton>
            <BaseButton size="small" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
          </div>
        </template>
      </div>
    </div>

    <!-- CREATOR FORM -->
    <div v-if="isCreating" class="creator-form">
       <div class="edit-container">
          <BaseInput v-model="newItem.name" ref="createInputRef" placeholder="New item name..." />
          <ColorSelector v-model="newItem.color" />
          <BaseButton size="small" @click="handleCreateItem" :loading="isSaving">Create</BaseButton>
          <BaseButton size="small" variant="secondary" @click="cancelCreating">Cancel</BaseButton>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="card-footer">
      <button v-if="!isCreating" @click="startCreating" class="create-btn">
        <PlusIcon class="icon" /> Create new {{ itemTypeName.toLowerCase() }}
      </button>
    </div>

    <!-- CONFIRMATION MODAL -->
    <ConfirmationModal
      :show="isDeleteModalVisible"
      :title="`Delete ${itemTypeName}`"
      :message="`Are you sure you want to delete '${itemToDelete?.name}'? This action cannot be undone.`"
      @close="isDeleteModalVisible = false"
      @confirm="handleDeleteItem"
    />
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';
import { PencilIcon, TrashIcon, PlusIcon } from '@heroicons/vue/24/outline';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  isSaving: { type: Boolean, default: false },
  itemTypeName: { type: String, required: true },
});

const emit = defineEmits(['create-item', 'update-item', 'delete-item']);

// --- LOCAL STATE ---
const isCreating = ref(false);
const editingItemId = ref(null);
const isDeleteModalVisible = ref(false);
const itemToDelete = ref(null);

const createInputRef = ref(null);
const editInputRef = ref(null);

const newItem = reactive({ name: '', color: '#888888' });
const editedItem = reactive({ id: null, name: '', color: '' });

// --- CREATION LOGIC ---
const startCreating = async () => {
  isCreating.value = true;
  await nextTick();
  createInputRef.value?.focus();
};

const cancelCreating = () => {
  isCreating.value = false;
  newItem.name = '';
  newItem.color = '#888888';
};

const handleCreateItem = () => {
  if (!newItem.name.trim()) return;
  emit('create-item', { ...newItem });
  cancelCreating();
};

// --- EDITING LOGIC ---
const startEditing = async (item) => {
  editingItemId.value = item.id;
  editedItem.id = item.id;
  editedItem.name = item.name;
  editedItem.color = item.color;
  await nextTick();
  editInputRef.value?.focus();
};

const cancelEditing = () => {
  editingItemId.value = null;
};

const handleUpdateItem = () => {
  if (!editedItem.name.trim()) return;
  emit('update-item', { ...editedItem });
  cancelEditing();
};

// --- DELETION LOGIC ---
const promptDelete = (item) => {
  itemToDelete.value = item;
  isDeleteModalVisible.value = true;
};

const handleDeleteItem = () => {
  if (!itemToDelete.value) return;
  emit('delete-item', itemToDelete.value.id);
  isDeleteModalVisible.value = false;
  itemToDelete.value = null;
};

</script>

<style scoped>
.simple-label-card {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  display: flex;
  flex-direction: column;
}
.card-header {
  padding: var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
}
.card-title {
  font: var(--semantic-font-style-heading-xl);
}
.state-container {
  padding: var(--semantic-size-inset-xl);
  text-align: center;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-base);
}
.items-list {
  display: flex;
  flex-direction: column;
}
.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
}
.item-row:last-child {
  border-bottom: none;
}
.item-details {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}
.item-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.item-name {
  font: var(--semantic-font-style-body-base);
}
.item-actions {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}
.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}
.action-btn:hover {
  color: var(--semantic-color-text-primary);
}
.icon {
  width: 1rem;
  height: 1rem;
}
.icon-danger {
  color: var(--semantic-color-text-danger);
}
.edit-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  width: 100%;
}
.creator-form {
  padding: var(--semantic-size-inset-md);
  border-top: 1px solid var(--semantic-color-border-default);
}
.card-footer {
  padding: var(--semantic-size-inset-sm);
  border-top: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-secondary);
}
.create-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-label-md);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
}
.create-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>