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
const isPopoverOpen = ref(false);
const popoverStyle = ref({});
const activeGroup = ref(null);
const selectedTagIdsInPopover = ref([]);
const popoverRef = ref(null);

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

const openPopover = async (event, group) => {
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

    popoverStyle.value = {
        position: 'fixed',
        top: `${rect.bottom + 8}px`,
        left: `${rect.right - 110}px`,
    };
    isPopoverOpen.value = true;
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

</script>

<template>
  <div class="tag-manager-section">
    <!-- Main UI -->
    <div v-for="group in allGroupedTags" :key="group.id" class="tag-group-row">
      <span class="group-name">{{ group.name }}</span>
      <div class="tags-container">
        <div class="tag-pills-display">
            <BasePill v-for="tag in group.tradeTags" :key="tag.id" :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }">
              {{ tag.name }}
            </BasePill>
            <p v-if="group.tradeTags.length === 0" class="no-tags-message">-</p>
        </div>
        <IconButton @click="openPopover($event, group)">
            <PlusIcon/>
        </IconButton>
      </div>
    </div>

    <!-- The single, shared popover with internal debug -->
    <div v-if="isPopoverOpen && activeGroup" :style="popoverStyle" class="popover-panel" ref="popoverRef">
        <div class="popover-content">
            <!-- ========= POPOVER-INTERNAL DEBUGGING ========= -->
            <div class="debug-section-internal">
                <h4>Active Group Tags ({{ activeGroup.tags.length }})</h4>
                <pre>{{ activeGroup.tags }}</pre>
            </div>
            <!-- ========= END POPOVER-INTERNAL DEBUGGING ========= -->

            <div class="tag-selection-list">
                <p v-if="activeGroup.tags.length === 0" class="no-tags-message">No tags in this group.</p>
                <div v-for="tag in activeGroup.tags" :key="tag.id">
                    Tag: {{ tag.name }} (ID: {{ tag.id }})
                </div>
            </div>
            <div class="popover-actions">
                <BaseButton variant="secondary" size="small" @click="handleCancel">Cancel</BaseButton>
                <BaseButton size="small" @click="handleSaveChanges" :loading="tradesStore.isTradeLoading">Save</BaseButton>
            </div>
        </div>
    </div>

    <!-- ========= MAIN DEBUGGING OUTPUT ========= -->
    <div class="debug-section">
        <hr>
        <h3>MAIN DEBUGGING SECTION</h3>
        <h4>Raw Tags from Store ({{ tagsStore.tags.length }})</h4>
        <pre>{{ tagsStore.tags }}</pre>
        <h4>Raw Tag Groups from Store ({{ tagsStore.tagGroups.length }})</h4>
        <pre>{{ tagsStore.tagGroups }}</pre>
        <hr>
    </div>
    <!-- ========= END DEBUGGING ========= -->
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

.debug-section, .debug-section-internal {
    background-color: #1a1a1a;
    color: #0f0;
    padding: 1rem;
    margin-top: 1rem;
    border: 1px solid #0f0;
    font-family: monospace;
    font-size: 12px;
    white-space: pre-wrap;
}
.debug-section-internal {
    background-color: #1a1a4a;
    border-color: #0ff;
    color: #0ff;
}
</style>