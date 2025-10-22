<template>
  <div class="management-card-container">
    <!-- Header -->
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
    </div>

    <!-- Confirmation Modal for Deletion -->
    <ConfirmationModal
      v-if="isDeleteModalVisible"
      :show="isDeleteModalVisible"
      title="Delete Item"
      :message="`Are you sure you want to delete this item? This action cannot be undone.`"
      @close="isDeleteModalVisible = false"
      @confirm="handleConfirmDelete"
    />

    <!-- Items List -->
    <div class="items-list">
      <template v-if="!isGrouped">
        <LibraryItemRow
          v-for="item in items"
          :key="item.id"
          :item="item"
          :is-saving="isSaving"
          @update="handleUpdate"
          @delete="promptDelete"
        />
      </template>
      <template v-else>
        <div v-for="group in items" :key="group.id" class="group-container">
          <h4 class="group-title">{{ group.name }}</h4>
          <LibraryItemRow
            v-for="item in group.news_impacts"
            :key="item.id"
            :item="item"
            :is-saving="isSaving"
            @update="handleUpdate"
            @delete="promptDelete"
          />
        </div>
      </template>
      <LibraryItemCreator
        v-if="isCreating"
        :is-saving="isSaving"
        :is-grouped="isGrouped"
        :groups="groups"
        @save="handleCreate"
        @cancel="isCreating = false"
      />
    </div>

    <!-- Footer -->
    <footer class="card-footer">
      <button class="create-item-btn" @click="isCreating = true">+ Create new</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, defineProps, computed } from 'vue';
import { useLibraryStore } from '@/stores/libraryStore';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import LibraryItemRow from './LibraryItemRow.vue';
import LibraryItemCreator from './LibraryItemCreator.vue';

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
  createAction: { type: Function, required: false },
  updateAction: { type: Function, required: false },
  deleteAction: { type: Function, required: false },
  isGrouped: { type: Boolean, default: false },
  isSaving: { type: Boolean, default: false },
});

const store = useLibraryStore();
const newsImpactsStore = useNewsImpactsStore();
const isCreating = ref(false);

// --- Deletion Logic ---
const isDeleteModalVisible = ref(false);
const itemToDelete = ref(null);

const promptDelete = (item) => {
  itemToDelete.value = item;
  isDeleteModalVisible.value = true;
};

const handleConfirmDelete = async () => {
  if (!itemToDelete.value) return;
  if (props.isGrouped) {
    await newsImpactsStore.deleteNewsImpact(itemToDelete.value.id);
  } else {
    await props.deleteAction(itemToDelete.value.id);
  }
  isDeleteModalVisible.value = false;
  itemToDelete.value = null;
};

// --- Create/Update Logic ---
const handleCreate = async (itemData) => {
  if (props.isGrouped) {
    await newsImpactsStore.createNewsImpact(itemData);
  } else {
    await props.createAction(itemData);
  }
  isCreating.value = false;
};

const handleUpdate = async ({ id, data }) => {
  if (props.isGrouped) {
    await newsImpactsStore.updateNewsImpact(id, data);
  } else {
    await props.updateAction(id, data);
  }
};

const groups = computed(() => {
  if (props.isGrouped) {
    return props.items.map(group => ({ id: group.id, name: group.name }));
  }
  return [];
});
</script>

<style scoped>
.management-card-container {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
  margin-bottom: var(--semantic-size-stack-md);
}

.card-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  flex-grow: 1;
}

.items-list {
  display: flex;
  flex-direction: column;
}

.card-footer {
  margin-top: var(--semantic-size-stack-sm);
}

.create-item-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-label-md);
  padding: var(--semantic-size-stack-xxs);
}

.create-item-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>