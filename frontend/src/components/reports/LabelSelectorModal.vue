<template>
  <BaseModal :show="show" @close="handleCancel" :title="`Select ${itemTypeName}s`">
    <div class="modal-content">
      <div class="search-bar">
        <BaseInput v-model="searchTerm" :placeholder="`Search ${itemTypeName.toLowerCase()}s...`" class="search-input" />
      </div>
      <div class="items-list">
        <div v-if="filteredItems.length === 0" class="no-results">
          No {{ itemTypeName.toLowerCase() }}s found.
        </div>
        <BaseCheckbox
          v-for="item in filteredItems"
          :key="item.id"
          :model-value="localSelectedIds.includes(item.id)"
          :label="item.name"
          @update:modelValue="toggleItem(item.id)"
          class="item-checkbox"
        />
      </div>
    </div>
    <template #footer>
      <BaseButton @click="handleCancel" variant="secondary">Cancel</BaseButton>
      <BaseButton @click="handleSave" variant="primary">Save</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, watch } from 'vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  show: { type: Boolean, required: true },
  title: { type: String, required: true },
  allItems: { type: Array, required: true },
  selectedIds: { type: Array, default: () => [] },
  itemTypeName: { type: String, default: 'Item' },
});

const emit = defineEmits(['close', 'save']);

const searchTerm = ref('');
const localSelectedIds = ref([]);

// Sync local state with props when the modal is shown
watch(() => props.show, (newVal) => {
  if (newVal) {
    localSelectedIds.value = [...props.selectedIds];
  }
}, { immediate: true });

const filteredItems = computed(() => {
  if (!searchTerm.value) return props.allItems;
  const lowerCaseSearch = searchTerm.value.toLowerCase();
  return props.allItems.filter(item => item.name.toLowerCase().includes(lowerCaseSearch));
});

const toggleItem = (itemId) => {
  const index = localSelectedIds.value.indexOf(itemId);
  if (index > -1) {
    localSelectedIds.value.splice(index, 1);
  } else {
    localSelectedIds.value.push(itemId);
  }
};

const handleSave = () => {
  emit('save', localSelectedIds.value);
  emit('close');
};

const handleCancel = () => {
  emit('close');
};
</script>

<style scoped>
.modal-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.search-bar {
  padding-bottom: var(--semantic-size-stack-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
}
.search-input {
  width: 100%;
}
.items-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
.item-checkbox {
  padding: var(--semantic-size-inset-sm);
  cursor: pointer;
  border-radius: var(--semantic-border-radius-interactive);
}
.item-checkbox:hover {
  background-color: var(--semantic-color-surface-hover);
}
.no-results {
  padding: var(--semantic-size-inset-lg);
  text-align: center;
  color: var(--semantic-color-text-secondary);
}
</style>