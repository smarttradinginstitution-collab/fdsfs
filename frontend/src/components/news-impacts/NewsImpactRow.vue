<template>
  <div class="impact-row" :class="{ 'is-editing': isEditing }">
    <div class="impact-content">
      <!-- Display State -->
      <template v-if="!isEditing">
        <BasePill :style="{ backgroundColor: impact.color, color: getTextColor(impact.color) }">
          {{ impact.name }}
        </BasePill>
      </template>
      <!-- Editing State -->
      <template v-else>
        <BaseInput
          ref="inputRef"
          v-model="editedName"
          class="inline-input"
        />
        <ColorSelector v-model="editedColor" />
      </template>
    </div>

    <!-- Actions -->
    <div class="impact-actions">
      <template v-if="!isEditing">
        <ActionsMenu>
          <template #default="{ closeMenu }">
            <div class="menu-item" @click="() => { startEditing(); closeMenu(); }">Edit</div>
            <div class="menu-item menu-item-danger" @click="() => { emit('delete', impact); closeMenu(); }">Delete</div>
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
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ActionsMenu from '@/components/ui/ActionsMenu.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import BasePill from '@/components/ui/BasePill.vue';

const props = defineProps({
  impact: { type: Object, required: true },
});

const emit = defineEmits(['delete']);

const store = useNewsImpactsStore();
const isSaving = computed(() => store.isSaving);

const isEditing = ref(false);
const editedName = ref('');
const editedColor = ref('');
const inputRef = ref(null);

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};

const startEditing = async () => {
  editedName.value = props.impact.name;
  editedColor.value = props.impact.color;
  isEditing.value = true;
  await nextTick();
  inputRef.value?.focus();
};

const cancelEditing = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  if (!editedName.value.trim()) return;
  const hasChanged = editedName.value.trim() !== props.impact.name || editedColor.value !== props.impact.color;
  if (hasChanged) {
    try {
      await store.updateNewsImpact(props.impact.id, {
        name: editedName.value,
        color: editedColor.value,
      });
    } catch (e) {
      console.error("Failed to update news impact:", e);
    }
  }
  isEditing.value = false;
};
</script>

<style scoped>
.impact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-surface);
}
.impact-row:last-child {
  border-bottom: none;
}

/* Styles for when the component is in editing mode */
.impact-row.is-editing {
  flex-direction: column;
  align-items: stretch;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-md);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  background-color: var(--semantic-color-surface-secondary);
}

.impact-content {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  flex-grow: 1;
}

/* When editing, the content also stacks vertically */
.impact-row.is-editing .impact-content {
  flex-direction: column;
  align-items: stretch;
}

.impact-actions {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

/* When editing, align action buttons to the end */
.impact-row.is-editing .impact-actions {
  justify-content: flex-end;
}

.inline-input {
  flex-grow: 1;
}
</style>