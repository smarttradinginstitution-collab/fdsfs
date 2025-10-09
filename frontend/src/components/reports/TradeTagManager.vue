<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import { useTradesStore } from '@/stores/trades';
import BasePill from '@/components/ui/BasePill.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';
import CloseIcon from '@/components/icons/CloseIcon.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const tagsStore = useTagsStore();
const tradesStore = useTradesStore();

// State for Add-Tag Popup
const editingGroupId = ref(null);
const selectedTagIdsInPopup = ref([]);

// State for Remove-Tag "Deletion Mode"
const deletingFromGroupId = ref(null);

onMounted(() => {
  if (tagsStore.tagGroups.length === 0 || tagsStore.tags.length === 0) {
    tagsStore.fetchAllTagsData();
  }
});

const allGroupedTags = computed(() => {
  const sortedGroups = [...tagsStore.tagGroups].sort((a, b) => a.order - b.order);
  return sortedGroups.map(group => ({
    ...group,
    tags: tagsStore.tags.filter(tag => tag.group_id === group.id),
    tradeTags: props.trade.tags.filter(tradeTag => tradeTag.group_id === group.id),
  }));
});

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};

// --- ADD TAG LOGIC ---
const openAddPopup = (group) => {
  deletingFromGroupId.value = null; // Exit delete mode if active
  editingGroupId.value = group.id;
  selectedTagIdsInPopup.value = group.tradeTags.map(t => t.id);
};

const closeAddPopup = () => {
  editingGroupId.value = null;
  selectedTagIdsInPopup.value = [];
};

const handleSaveChanges = async () => {
  if (!editingGroupId.value) return;
  const otherGroupTagIds = props.trade.tags
    .filter(tag => tag.group_id !== editingGroupId.value)
    .map(tag => tag.id);
  const finalTagIds = [...otherGroupTagIds, ...selectedTagIdsInPopup.value];
  await tradesStore.updateTradeTags(props.trade.id, finalTagIds);
  closeAddPopup();
};

// --- REMOVE TAG LOGIC ---
const enterDeleteMode = (groupId) => {
  if (editingGroupId.value) return; // Don't enter delete mode if popup is open
  deletingFromGroupId.value = groupId;
};

const exitDeleteMode = () => {
  deletingFromGroupId.value = null;
};

const removeTag = async (tagToRemove) => {
  const currentTagIds = props.trade.tags.map(t => t.id);
  const finalTagIds = currentTagIds.filter(id => id !== tagToRemove.id);
  await tradesStore.updateTradeTags(props.trade.id, finalTagIds);

  // If the last tag of the group was removed, exit delete mode automatically
  const remainingTags = props.trade.tags.filter(t => t.group_id === tagToRemove.group_id);
  if (remainingTags.length === 0) {
    exitDeleteMode();
  }
};

</script>

<template>
  <div class="tag-manager-section">
    <!-- Rows for each tag group -->
    <div v-for="group in allGroupedTags" :key="group.id" class="tag-group-row">
      <span class="group-name">{{ group.name }}</span>
      <div class="tags-container" @click="deletingFromGroupId === group.id && exitDeleteMode()">
        <div class="tag-pills-display">
          <div
            v-for="tag in group.tradeTags"
            :key="tag.id"
            class="tag-pill-wrapper"
            @click.stop="enterDeleteMode(group.id)"
          >
            <BasePill
              :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }"
              class="tag-pill"
            >
              {{ tag.name }}
            </BasePill>
            <button
              v-if="deletingFromGroupId === group.id"
              class="delete-tag-btn"
              @click.stop="removeTag(tag)"
            >
              <CloseIcon />
            </button>
          </div>
          <p v-if="group.tradeTags.length === 0" class="no-tags-message">-</p>
        </div>
        <IconButton v-if="deletingFromGroupId !== group.id" @click.stop="openAddPopup(group)">
          <PlusIcon />
        </IconButton>
        <BaseButton v-else variant="secondary" size="small" @click.stop="exitDeleteMode">Done</BaseButton>
      </div>
    </div>

    <!-- Add/Edit Tags Modal -->
    <BaseModal :show="!!editingGroupId" @close="closeAddPopup">
      <template #header>
        <h3>Add Tags to Group</h3>
      </template>
      <template #body>
        <div v-if="editingGroupId" class="tag-selection-list">
          <BaseCheckbox
            v-for="tag in allGroupedTags.find(g => g.id === editingGroupId).tags"
            :key="tag.id"
            :id="`tag-${tag.id}`"
            :value="tag.id"
            v-model="selectedTagIdsInPopup"
          >
            {{ tag.name }}
          </BaseCheckbox>
        </div>
      </template>
      <template #footer>
        <div class="modal-actions">
          <BaseButton variant="secondary" @click="closeAddPopup">Cancel</BaseButton>
          <BaseButton @click="handleSaveChanges" :loading="tradesStore.isTradeLoading">Save Changes</BaseButton>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<style lang="scss" scoped>
.tag-manager-section {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  margin-top: var(--semantic-size-stack-lg);
}

.tag-group-row {
  display: grid;
  grid-template-columns: 40% 1fr;
  gap: var(--semantic-size-stack-md);
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

.group-name {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  justify-self: start;
}

.tags-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tag-pills-display {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
  align-items: center;
}

.no-tags-message {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin: 0;
}

.tag-pill-wrapper {
  position: relative;
  display: inline-block;
  .tag-pill {
    cursor: pointer;
  }
}

.delete-tag-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  background-color: var(--semantic-color-surface-sunken);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  color: var(--semantic-color-text-secondary);
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--semantic-color-background-muted);
    color: var(--semantic-color-text-primary);
    transform: scale(1.1);
  }

  :deep(svg) {
    width: 10px;
    height: 10px;
  }
}

.tag-selection-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>