<template>
  <div class="tag-management-container">
    <!-- INLINE GROUP CREATOR -->
    <GroupCreator v-if="store.isCreatingGroup" />

    <!-- LOADING/ERROR STATES -->
    <div v-if="isLoading" class="loading-state"><LoadingSpinner /></div>
    <div v-else-if="error" class="error-state"><p>Error loading tags: {{ error }}</p></div>

    <!-- CONTENT -->
    <draggable
      v-else
      v-model="localGroupedTags"
      class="content-container"
      item-key="id"
      handle=".drag-handle"
      @end="onGroupDragEnd"
    >
      <template #item="{ element: group }">
        <TagGroup :group="group" />
      </template>
    </draggable>
    <div v-if="!localGroupedTags.length && !store.isCreatingGroup && !isLoading" class="empty-state">
        <p>No tag groups have been created yet.</p>
        <p>Click "+ Add Group" to get started.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref, watch } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import GroupCreator from '@/components/tags/GroupCreator.vue';
import TagGroup from '@/components/tags/TagGroup.vue';
import draggable from 'vuedraggable';

const store = useTagsStore();
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

// Local state for vuedraggable
const localGroupedTags = ref([]);
watch(() => store.groupedTags, (newGroups) => {
    localGroupedTags.value = [...newGroups];
}, { immediate: true, deep: true });

const onGroupDragEnd = async () => {
    const groupIds = localGroupedTags.value.map(group => group.id);
    await store.reorderTagGroups(groupIds);
};

onMounted(() => {
  store.fetchAllTagsData();
  // Ensure creator is hidden on mount
  store.setCreatingGroup(false);
  store.setCreatingTagInGroup(null);
});
</script>

<style scoped>
.tag-management-container {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.loading-state, .error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}
.content-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
}
</style>