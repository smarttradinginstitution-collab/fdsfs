<template>
  <div class="playbook-content-tab">
    <div v-if="!playbook" class="loading-state">
      <p>Loading content...</p>
    </div>
    <div v-else class="content-container space-y-4">
      <div v-for="(block, index) in playbook.blocks" :key="index">
        <component
          :is="blockComponentMap[block.block_type]"
          :content="block.content"
          :conditions="playbook.conditions"
          class="read-only-block"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import ThesisEditor from './ThesisEditor.vue';
import GalleryEditor from './GalleryEditor.vue';

const props = defineProps({
  playbook: {
    type: Object,
    required: true,
  },
});

import RulesEditor from './RulesEditor.vue';

const blockComponentMap = {
  RULES: RulesEditor,
  THESIS: ThesisEditor,
  GALLERY: GalleryEditor,
};
</script>

<style scoped>
.playbook-content-tab {
  padding: 1rem;
}
.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--semantic-color-text-secondary);
}
.content-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.read-only-block {
  pointer-events: none; /* Make blocks read-only */
  opacity: 0.9;
}
</style>
