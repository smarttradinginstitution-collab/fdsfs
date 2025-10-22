<template>
  <div class="news-impact-group-container">
    <!-- Group Header -->
    <div class="group-header">
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
        <BaseButton size="small" @click="saveGroupEdit" :is-loading="isSaving">Save</BaseButton>
        <BaseButton size="small" variant="secondary" @click="cancelGroupEditing">Cancel</BaseButton>
      </div>
    </div>

    <!-- Modals for Deletion Confirmation -->
    <ConfirmationModal
      v-if="isGroupDeleteModalVisible"
      :show="isGroupDeleteModalVisible"
      title="Delete Group"
      :message="`Are you sure you want to delete the group '${group.name}'? This will also delete all impacts within it.`"
      @close="isGroupDeleteModalVisible = false"
      @confirm="handleConfirmDeleteGroup"
    />
    <ConfirmationModal
      v-if="isImpactDeleteModalVisible"
      :show="isImpactDeleteModalVisible"
      title="Delete News Impact"
      message="Are you sure you want to delete this news impact? This action cannot be undone."
      @close="isImpactDeleteModalVisible = false"
      @confirm="handleConfirmDeleteImpact"
    />

    <!-- Impacts List -->
    <div class="impacts-list">
      <NewsImpactRow
        v-for="impact in group.news_impacts"
        :key="impact.id"
        :impact="impact"
        @delete="promptDeleteImpact"
      />
      <NewsImpactCreator v-if="store.creatingTagInGroupId === group.id" :group-id="group.id" />
    </div>

    <!-- Footer -->
    <footer class="group-footer">
      <button class="create-impact-btn" @click="store.setCreatingTagInGroup(group.id)">+ Create new impact</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, defineProps, nextTick, computed } from 'vue';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import NewsImpactRow from './NewsImpactRow.vue';
import NewsImpactCreator from './NewsImpactCreator.vue';

const props = defineProps({
  group: { type: Object, required: true },
});

const store = useNewsImpactsStore();
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
  await store.updateNewsImpactGroup(props.group.id, { name: editedGroupName.value });
  isEditingGroup.value = false;
};

// Deletion Modals State
const isGroupDeleteModalVisible = ref(false);
const isImpactDeleteModalVisible = ref(false);
const impactToDelete = ref(null);

const handleConfirmDeleteGroup = async () => {
  await store.deleteNewsImpactGroup(props.group.id);
  isGroupDeleteModalVisible.value = false;
};

const promptDeleteImpact = (impact) => {
  impactToDelete.value = impact;
  isImpactDeleteModalVisible.value = true;
};

const handleConfirmDeleteImpact = async () => {
  if (!impactToDelete.value) return;
  await store.deleteNewsImpact(impactToDelete.value.id);
  isImpactDeleteModalVisible.value = false;
  impactToDelete.value = null;
};
</script>

<style scoped>
.news-impact-group-container {
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

.impacts-list {
  display: flex;
  flex-direction: column;
}

.group-footer {
  margin-top: var(--semantic-size-stack-sm);
}

.create-impact-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  font: var(--semantic-font-style-label-md);
  padding: var(--semantic-size-stack-xxs);
}

.create-impact-btn:hover {
  color: var(--semantic-color-text-primary);
}
</style>