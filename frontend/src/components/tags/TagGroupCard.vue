<script setup>
import { ref } from "vue";
import BaseWidget from "@/components/layout/BaseWidget.vue";
import TagChip from "./TagChip.vue";
import IconButton from "@/components/ui/IconButton.vue";
import PlusIcon from "@/components/icons/PlusIcon.vue";
import PencilIcon from "@/components/icons/PencilIcon.vue";
import TrashIcon from "@/components/icons/TrashIcon.vue";
import CreateOrEditTagModal from "./CreateOrEditTagModal.vue";

const props = defineProps({
  group: {
    type: Object,
    required: true,
  },
  tags: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['edit-group', 'delete-group', 'edit-tag', 'delete-tag']);

const isTagModalOpen = ref(false);

const openAddTagModal = () => {
  isTagModalOpen.value = true;
};

const handleEditGroup = () => {
  emit('edit-group', props.group);
}

const handleDeleteGroup = () => {
  emit('delete-group', props.group);
}

const handleEditTag = (tag) => {
  emit('edit-tag', tag);
}

const handleDeleteTag = (tag) => {
  emit('delete-tag', tag);
}

</script>

<template>
  <BaseWidget class="tag-group-card">
    <template #title>{{ group.name_group }}</template>
    <template #actions>
      <IconButton @click="handleEditGroup" tooltip="Edit Group">
        <PencilIcon />
      </IconButton>
      <IconButton @click="handleDeleteGroup" tooltip="Delete Group" variant="danger">
        <TrashIcon />
      </IconButton>
      <IconButton @click="openAddTagModal" tooltip="Add Tag">
        <PlusIcon />
      </IconButton>
    </template>
    <template #content>
      <div v-if="tags.length > 0" class="tags-container">
        <TagChip
          v-for="tag in tags"
          :key="tag.id"
          :tag="tag"
          @edit="handleEditTag"
          @delete="handleDeleteTag"
        />
      </div>
      <div v-else class="no-tags-message">
        <p>No tags in this group yet.</p>
      </div>
    </template>
  </BaseWidget>
  <CreateOrEditTagModal
    v-model="isTagModalOpen"
    :group-id="props.group.id"
  />
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