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

const localBlock = ref(JSON.parse(JSON.stringify(props.block)));

const blockComponentMap = {
  THESIS: ThesisEditor,
  GALLERY: GalleryEditor,
  CONDITIONS: RulesEditor,
  PSYCHOLOGY: RulesEditor, // Placeholder, uses RulesEditor for now
  LEGACY_RULES: RulesEditor, // Placeholder, uses RulesEditor for now
};

const currentEditor = computed(() => {
    return blockComponentMap[localBlock.value.block_type] || null;
});

const saveTitle = async () => {
  uiStore.showLoader();
  try {
    await playbookStore.updateBlock(playbookId.value, localBlock.value.id, {
        title: localBlock.value.title,
        content: localBlock.value.content, // Pass content along to be safe
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
        :blockId="localBlock.id"
        :blockTitle="localBlock.title"
      />
      <div v-else class="unknown-block-type">
        <p>Unsupported block type: "{{ localBlock.block_type }}"</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
.unknown-block-type {
    text-align: center;
    color: var(--semantic-color-text-subtle);
    padding: var(--semantic-size-inset-lg);
}
</style>
