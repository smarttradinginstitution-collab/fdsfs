<script setup>
import BaseWidget from "@/components/layout/BaseWidget.vue";
import TagChip from "./TagChip.vue";

defineProps({
  group: {
    type: Object,
    required: true,
  },
  tags: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <BaseWidget class="tag-group-card">
    <template #title>{{ group.name_group }}</template>
    <template #content>
      <div v-if="tags.length > 0" class="tags-container">
        <TagChip v-for="tag in tags" :key="tag.id" :tag="tag" />
      </div>
      <div v-else class="no-tags-message">
        <p>No tags in this group yet.</p>
      </div>
    </template>
  </BaseWidget>
</template>

<style lang="scss" scoped>
.tag-group-card {
  /* The BaseWidget provides the main structure and padding */
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}

.no-tags-message {
  p {
    font: var(--semantic-font-style-body-md);
    color: var(--semantic-color-text-disabled);
    font-style: italic;
  }
}
</style>