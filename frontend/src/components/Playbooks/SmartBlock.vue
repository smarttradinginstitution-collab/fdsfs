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
  RULES: RulesEditor,
  THESIS: ThesisEditor,
  GALLERY: GalleryEditor,
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
      <input v-model="localBlock.title" @blur="saveTitle" class="input-ghost block-title-input" />
      <IconButton @click="deleteThisBlock" ariaLabel="Delete Block" class="delete-button">
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
    background-color: #15171B; /* New, darker card background */
    border-radius: 12px;
    margin-bottom: 1rem; /* 16px */
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 1.5rem; /* 24px */
}
.block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.block-header .delete-button {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}
.smart-block:hover .delete-button {
    opacity: 1;
}
.block-title-input {
    font-size: 18px;
    font-weight: 600; /* semibold */
}
.block-content {
    padding: 0; /* Content spacing is handled by children */
}
.unknown-block-type {
    text-align: center;
    color: var(--semantic-color-text-subtle);
    padding: var(--semantic-size-inset-lg);
}
</style>
