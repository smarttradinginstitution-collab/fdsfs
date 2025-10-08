<template>
  <div class="tag-row">
    <div class="tag-content">
      <div class="color-dot" :style="{ backgroundColor: tag.color }"></div>
      <template v-if="!isEditing">
        <span class="tag-name">{{ tag.name }}</span>
      </template>
      <template v-else>
        <BaseInput
          ref="inputRef"
          v-model="editedName"
          class="inline-input"
        />
        <ColorSelector v-model="editedColor" />
      </template>
    </div>
    <div class="tag-actions">
      <template v-if="!isEditing">
        <ActionsMenu>
          <template #default="{ closeMenu }">
            <div class="menu-item" @click="() => { startEditing(); closeMenu(); }">Edit</div>
            <div class="menu-item menu-item-danger" @click="() => { emit('delete', tag); closeMenu(); }">Delete</div>
          </template>
        </ActionsMenu>
      </template>
      <template v-else>
        <BaseButton size="small" @click="saveEdit" :loading="isSaving">Save</BaseButton>
        <BaseButton size="small" variant="secondary" @click="cancelEditing">Cancel</BaseButton>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, defineProps, defineEmits, computed } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';

const props = defineProps({
  tag: { type: Object, required: true },
});

const emit = defineEmits(['delete']);

const store = useTagsStore();
const isSaving = computed(() => store.isSaving);

const isEditing = ref(false);
const editedName = ref('');
const editedColor = ref('');
const inputRef = ref(null);

const startEditing = async () => {
  editedName.value = props.tag.name;
  editedColor.value = props.tag.color;
  isEditing.value = true;
  await nextTick();
  inputRef.value?.focus();
};

const cancelEditing = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  if (!editedName.value.trim()) return;

  const hasChanged = editedName.value.trim() !== props.tag.name || editedColor.value !== props.tag.color;

  if (hasChanged) {
    try {
      await store.updateTag(props.tag.id, {
        name: editedName.value,
        color: editedColor.value,
      });
    } catch (e) {
      console.error("Failed to update tag:", e);
      // Optionally, revert changes on failure, though the store refresh will do this.
    }
  }
  isEditing.value = false;
};
</script>

<style scoped>
.tag-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-muted);
}

.tag-row:last-child {
  border-bottom: none;
}

.tag-content {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  flex-grow: 1;
}

.color-dot {
  width: var(--base-size-spacing-3);
  height: var(--base-size-spacing-3);
  border-radius: var(--base-border-radius-full);
  flex-shrink: 0;
}

.tag-name {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
}

.tag-actions {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.inline-input {
  flex-grow: 1;
}
</style>