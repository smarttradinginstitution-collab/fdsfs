<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import { useTradesStore } from '@/stores/trades';
import { onClickOutside } from '@vueuse/core';

import BasePill from '@/components/ui/BasePill.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import CloseIcon from '@/components/icons/CloseIcon.vue';
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const tagsStore = useTagsStore();
const tradesStore = useTradesStore();

// --- STATE ---
const popoverRef = ref(null);
const isPopoverOpen = ref(false);
const popoverStyle = ref({});
const activeGroup = ref(null);
const selectedTagIdsInPopover = ref([]);
const deletingFromGroupId = ref(null);

// --- LIFECYCLE ---
onMounted(() => {
  if (tagsStore.tagGroups.length === 0 || tagsStore.tags.length === 0) {
    tagsStore.fetchAllTagsData();
  }
});

onClickOutside(popoverRef, () => {
    if (isPopoverOpen.value) {
        isPopoverOpen.value = false;
        activeGroup.value = null;
    }
});

// --- COMPUTED ---
const allGroupedTags = computed(() => {
  if (!tagsStore.tagGroups || !tagsStore.tags) return [];
  const sortedGroups = [...tagsStore.tagGroups].sort((a, b) => a.order - b.order);
  return sortedGroups.map(group => ({
    ...group,
    tags: tagsStore.tags.filter(tag => tag.group_id === group.id),
    tradeTags: props.trade.tags.filter(tradeTag => tradeTag.group_id === group.id),
  }));
});

// --- METHODS ---
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
const openPopover = async (event, group) => {
    if (deletingFromGroupId.value) return;

    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();

    if (activeGroup.value?.id === group.id) {
        isPopoverOpen.value = false;
        activeGroup.value = null;
        return;
    }

    isPopoverOpen.value = false;
    await nextTick();

    activeGroup.value = group;
    selectedTagIdsInPopover.value = group.tradeTags.map(t => t.id);
    isPopoverOpen.value = true;

    await nextTick();

    const popoverEl = popoverRef.value;
    if (!popoverEl) return;

    const popoverRect = popoverEl.getBoundingClientRect();
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;

    let top = rect.bottom + 8;
    let left = rect.left + (rect.width / 2) - (popoverRect.width / 2);

    if (left < 0) left = 8;
    if (left + popoverRect.width > windowWidth) left = windowWidth - popoverRect.width - 8;
    if (top + popoverRect.height > windowHeight) top = rect.top - popoverRect.height - 8;

    popoverStyle.value = {
        position: 'fixed',
        top: `${top}px`,
        left: `${left}px`,
    };
};

const handleSaveChanges = async () => {
  if (!activeGroup.value) return;
  const otherGroupTagIds = props.trade.tags.filter(tag => tag.group_id !== activeGroup.value.id).map(tag => tag.id);
  const finalTagIds = [...otherGroupTagIds, ...selectedTagIdsInPopover.value];
  await tradesStore.updateTradeTags(props.trade.id, finalTagIds);
  isPopoverOpen.value = false;
  activeGroup.value = null;
};

const handleCancel = () => {
  isPopoverOpen.value = false;
  activeGroup.value = null;
};

// --- REMOVE TAG LOGIC ---
const enterDeleteMode = (groupId) => {
  if (isPopoverOpen.value) return;
  deletingFromGroupId.value = groupId;
};

const exitDeleteMode = () => {
  deletingFromGroupId.value = null;
};

const removeTag = async (tagToRemove) => {
  const currentTagIds = props.trade.tags.map(t => t.id);
  const finalTagIds = currentTagIds.filter(id => id !== tagToRemove.id);
  await tradesStore.updateTradeTags(props.trade.id, finalTagIds);

  const remainingTags = props.trade.tags.filter(t => t.group_id === tagToRemove.group_id && t.id !== tagToRemove.id);
  if (remainingTags.length === 0) {
    exitDeleteMode();
  }
};
</script>

<template>
  <div class="tag-manager-section">
    <div v-for="group in allGroupedTags" :key="group.id" class="tag-group-row">
      <span class="group-name">{{ group.name }}</span>
      <div class="tags-container">
        <div class="tag-pills-display">
            <div
                v-for="tag in group.tradeTags"
                :key="tag.id"
                class="tag-pill-wrapper"
                @click.stop="enterDeleteMode(group.id)"
            >
                <BasePill :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }" class="tag-pill">
                  {{ tag.name }}
                </BasePill>
                <button v-if="deletingFromGroupId === group.id" class="delete-tag-btn" @click.stop="removeTag(tag)">
                    <CloseIcon />
                </button>
            </div>
            <p v-if="group.tradeTags.length === 0" class="no-tags-message">-</p>
        </div>

        <IconButton v-if="deletingFromGroupId !== group.id" @click="openPopover($event, group)">
            <PlusIcon/>
        </IconButton>
        <BaseButton v-else variant="secondary" size="small" @click.stop="exitDeleteMode">Done</BaseButton>

      </div>
    </div>

    <div v-if="isPopoverOpen && activeGroup" :style="popoverStyle" class="popover-panel" ref="popoverRef">
        <div class="popover-content">
            <div class="tag-selection-list">
                <p v-if="activeGroup.tags.length === 0" class="no-tags-message">No tags in this group.</p>
                <BaseCheckbox
                    v-for="tag in activeGroup.tags"
                    :key="tag.id"
                    :value="tag.id"
                    v-model="selectedTagIdsInPopover"
                >
                    {{ tag.name }}
                </BaseCheckbox>
            </div>
            <div class="popover-actions">
                <BaseButton variant="secondary" size="small" @click="handleCancel">Cancel</BaseButton>
                <BaseButton size="small" @click="handleSaveChanges" :loading="tradesStore.isTradeLoading">Save</BaseButton>
            </div>
        </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tag-manager-section {
  display: flex;
  flex-direction: column;

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
  padding: 0 var(--semantic-size-inset-sm);
}

.popover-panel {
  z-index: 20;
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
}

.popover-content {
    padding: var(--semantic-size-inset-md);
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-md);
    width: 220px;
}
.tag-selection-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
.popover-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  border-top: 1px solid var(--semantic-color-border-subtle);
  padding-top: var(--semantic-size-inset-md);
  margin-top: var(--semantic-size-inset-sm);
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
</style>