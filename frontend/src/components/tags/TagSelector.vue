<template>
  <div class="tag-selector">
    <PopoverMenu>
      <template #trigger="{ toggle }">
        <button @click="toggle" class="selector-trigger" type="button">
          <div v-if="selectedTags.length === 0" class="placeholder">Select tags...</div>
          <div v-else class="pills-container">
            <BasePill
              v-for="tag in selectedTags"
              :key="tag.id"
              :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }"
              class="trigger-pill"
            >
              {{ tag.name }}
            </BasePill>
          </div>
          <ChevronDownIcon class="trigger-icon" />
        </button>
      </template>

      <template #content>
        <div class="popover-content">
          <div class="search-bar">
            <BaseInput v-model="searchTerm" placeholder="Search tags..." class="search-input" />
          </div>

          <!-- Inline Creator -->
          <div v-if="isCreating" class="inline-creator">
            <ColorSelector v-model="newTagColor" />
            <div class="creator-actions">
              <BaseButton size="small" variant="secondary" @click="cancelCreation">Cancel</BaseButton>
              <BaseButton size="small" @click="handleCreateTag" :loading="store.isSaving">Create</BaseButton>
            </div>
          </div>

          <!-- Tags List -->
          <div class="tags-list">
            <div v-for="group in filteredGroupedTags" :key="group.id" class="tag-group">
              <h4 class="group-name">{{ group.name }}</h4>
              <ul>
                <li v-for="tag in group.tags" :key="tag.id" class="tag-item">
                  <BaseCheckbox :model-value="isSelected(tag.id)" :label="tag.name" @update:modelValue="toggleTag(tag.id)" />
                </li>
              </ul>
            </div>

            <!-- No Results & Create Button -->
            <div v-if="filteredGroupedTags.length === 0 && !isCreating" class="no-results">
              <p>No tags found for "{{ searchTerm }}".</p>
              <button @click="startCreation" class="create-button">
                <PlusIcon class="w-4 h-4 mr-1" /> Create new tag
              </button>
            </div>
          </div>
        </div>
      </template>
    </PopoverMenu>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineProps, defineEmits } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import PopoverMenu from '@/components/ui/PopoverMenu.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import { ChevronDownIcon, PlusIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});
const emit = defineEmits(['update:modelValue']);

const store = useTagsStore();
const searchTerm = ref('');
const isCreating = ref(false);
const newTagColor = ref('#4A90E2');

onMounted(() => {
  if (store.tags.length === 0 || store.tagGroups.length === 0) {
    store.fetchAllTagsData();
  }
});

const filteredGroupedTags = computed(() => {
  if (!searchTerm.value) return store.groupedTags;
  const lowerCaseSearch = searchTerm.value.toLowerCase();
  return store.groupedTags
    .map(group => ({
      ...group,
      tags: group.tags.filter(tag => tag.name.toLowerCase().includes(lowerCaseSearch)),
    }))
    .filter(group => group.tags.length > 0);
});

const selectedTags = computed(() => {
  return store.tags.filter(tag => props.modelValue.includes(tag.id));
});

const isSelected = (tagId) => props.modelValue.includes(tagId);

const toggleTag = (tagId) => {
  const newSelection = [...props.modelValue];
  const index = newSelection.indexOf(tagId);
  if (index > -1) {
    newSelection.splice(index, 1);
  } else {
    newSelection.push(tagId);
  }
  emit('update:modelValue', newSelection);
};

const startCreation = () => {
  isCreating.value = true;
};

const cancelCreation = () => {
  isCreating.value = false;
};

const handleCreateTag = async () => {
  if (!searchTerm.value.trim() || !store.tagGroups.length) return;

  // For simplicity, add the new tag to the first group.
  // A more advanced implementation could let the user choose.
  const targetGroupId = store.tagGroups[0].id;

  try {
    const newTag = await store.createTag({
      name: searchTerm.value,
      color: newTagColor.value,
      group_id: targetGroupId,
    });

    // Add the new tag to the selection automatically
    if (newTag && !isSelected(newTag.id)) {
      toggleTag(newTag.id);
    }

    // Reset state
    searchTerm.value = '';
    isCreating.value = false;
    newTagColor.value = '#4A90E2';

  } catch (error) {
    console.error("Failed to create tag from selector:", error);
  }
};

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
.selector-trigger {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  text-align: left; cursor: pointer;
}
.placeholder { color: var(--semantic-color-text-placeholder); }
.pills-container { display: flex; flex-wrap: wrap; gap: var(--semantic-size-stack-xs); flex-grow: 1; }
.trigger-pill { font-size: var(--semantic-font-style-body-sm); padding: 2px 8px; }
.trigger-icon { width: 1.25rem; height: 1.25rem; color: var(--semantic-color-text-secondary); margin-left: var(--semantic-size-stack-sm); }
.popover-content { display: flex; flex-direction: column; width: 300px; }
.search-bar { padding: var(--semantic-size-inset-sm); border-bottom: 1px solid var(--semantic-color-border-default); }
.search-input { width: 100%; }
.tags-list { max-height: 300px; overflow-y: auto; padding: var(--semantic-size-inset-sm); }
.tag-group { margin-bottom: var(--semantic-size-stack-sm); }
.group-name { font: var(--semantic-font-style-label-md); color: var(--semantic-color-text-secondary); padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm); }
.tag-item { padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm); cursor: pointer; border-radius: var(--semantic-border-radius-interactive); }
.tag-item:hover { background-color: var(--semantic-color-surface-hover); }
.no-results { padding: var(--semantic-size-inset-lg); text-align: center; color: var(--semantic-color-text-secondary); }
.create-button {
  background: none; border: none; color: var(--semantic-color-text-interactive);
  cursor: pointer; font: var(--semantic-font-style-label-md);
  display: inline-flex; align-items: center; padding: var(--semantic-size-stack-xs);
  margin-top: var(--semantic-size-stack-sm);
}
.create-button:hover { text-decoration: underline; }
.inline-creator {
  padding: var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-secondary);
  border-bottom: 1px solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
.creator-actions { display: flex; justify-content: flex-end; gap: var(--semantic-size-stack-sm); }
</style>