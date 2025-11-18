
<script setup>
import { ref, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import { useRoute } from 'vue-router';
import BaseInput from '@/components/ui/BaseInput.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';

// Import the specific block editors
import RulesEditor from './RulesEditor.vue';
import ThesisEditor from './ThesisEditor.vue';
import GalleryEditor from './GalleryEditor.vue';

const props = defineProps({
  block: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['delete-block']);

const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();
const playbookId = computed(() => route.params.id);

// Use a deep copy for local editing to avoid prop mutation
const localBlock = ref(JSON.parse(JSON.stringify(props.block)));

const blockComponentMap = {
  RULES: RulesEditor,
  THESIS: ThesisEditor,
  GALLERY: GalleryEditor,
  CONDITIONS: RulesEditor, // Assuming CONDITIONS uses the same editor as RULES
  PSYCHOLOGY: RulesEditor, // Placeholder
  LEGACY_RULES: RulesEditor // Placeholder
};

const currentEditor = computed(() => {
    return blockComponentMap[localBlock.value.block_type] || null;
});

const saveTitle = async () => {
  uiStore.showLoader();
  try {
    await playbookStore.updateBlock(playbookId.value, localBlock.value.id, {
        title: localBlock.value.title,
        // Send other fields if necessary, but here we only save the title
    });
  } catch (error) {
    console.error('Failed to save block title:', error);
  } finally {
    uiStore.hideLoader();
  }
};

const deleteThisBlock = () => {
    if (confirm(`Are you sure you want to delete the block "${props.block.title}"?`)) {
        emit('delete-block', props.block.id);
    }
};

</script>

<template>
  <div class="smart-block">
    <div class="block-header">
      <BaseInput v-model="localBlock.title" @blur="saveTitle" class="block-title-input" />
      <IconButton @click="deleteThisBlock" ariaLabel="Delete Block">
        <TrashIcon />
      </IconButton>
    </div>

    <div class="block-content">
      <component
        v-if="currentEditor"
        :is="currentEditor"
        :content="localBlock.content"
      />
      <div v-else class="unknown-block-type">
        <p>Unknown block type: {{ localBlock.block_type }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Main Block Styles */
.smart-block {
    background-color: var(--semantic-color-surface-primary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    margin-bottom: var(--semantic-size-stack-lg);
}
.block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
    background-color: var(--semantic-color-surface-subtle);
    border-bottom: 1px solid var(--semantic-color-border-default);
}
.block-title-input {
    font: var(--semantic-font-style-headline-sm);
    border: none;
    background: transparent;
    padding: 0;
}
.block-content {
    padding: var(--semantic-size-inset-md);
}

/* Group Styles */
.condition-group {
  background-color: var(--semantic-color-surface-subtle);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-md);
  border: 1px solid var(--semantic-color-border-subtle);
}
.group-header {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-inline-sm);
    margin-bottom: var(--semantic-size-stack-md);
}
.group-title-input {
  font: var(--semantic-font-style-body-lg-bold);
  border: none;
  background: transparent;
  padding: 0;
  flex-grow: 1;
}

/* Item Styles */
.items-list {
    min-height: 20px; /* Drop zone for draggable */
}
.list-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inline-sm);
  padding: var(--semantic-size-inset-xs);
  margin-bottom: var(--semantic-size-stack-xs);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-element);
  border: 1px solid var(--semantic-color-border-default);
}
.item-handle, .group-handle {
    cursor: grab;
    color: var(--semantic-color-text-subtle);
    padding: 0 var(--semantic-size-inline-sm);
}
.condition-text {
  display: flex; align-items: center; gap: var(--semantic-size-inline-sm); flex-grow: 1; font-family: monospace;
}
.checklist-text {
  display: flex; align-items: center; gap: var(--semantic-size-inline-sm); flex-grow: 1;
}
.checklist-input {
    border: none; background: transparent; padding: 0; width: 100%;
}
.delete-item-btn { margin-left: auto; }
.add-item-buttons {
  display: flex; gap: var(--semantic-size-inline-md); margin-top: var(--semantic-size-stack-md); border-top: 1px solid var(--semantic-color-border-subtle); padding-top: var(--semantic-size-stack-md);
}
.add-group-button {
  margin-top: var(--semantic-size-stack-md); display: block; margin-left: auto; margin-right: auto;
}
.no-items-message {
    font-style: italic; color: var(--semantic-color-text-subtle); text-align: center; padding: var(--semantic-size-inset-md);
}

/* Modal Styles */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.5); display: flex;
    justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
    background-color: var(--semantic-color-surface-primary);
    padding: var(--semantic-size-inset-lg);
    border-radius: var(--semantic-border-radius-surface);
    min-width: 400px; display: flex; flex-direction: column; gap: var(--semantic-size-stack-md);
}
.modal-actions {
    display: flex; justify-content: flex-end; gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-md);
}
</style>
