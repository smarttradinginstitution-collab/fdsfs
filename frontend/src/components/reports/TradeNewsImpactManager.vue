<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
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

const newsImpactsStore = useNewsImpactsStore();
const tradesStore = useTradesStore();

// --- STATE ---
const popoverRef = ref(null);
const isPopoverOpen = ref(false);
const popoverStyle = ref({});
const activeGroup = ref(null);
const selectedImpactIdsInPopover = ref([]);
const deletingFromGroupId = ref(null);

// --- LIFECYCLE ---
onMounted(() => {
  if (newsImpactsStore.newsImpactsGroups.length === 0 || newsImpactsStore.newsImpacts.length === 0) {
    newsImpactsStore.fetchAllNewsImpactsData();
  }
});

onClickOutside(popoverRef, () => {
    if (isPopoverOpen.value) {
        isPopoverOpen.value = false;
        activeGroup.value = null;
    }
});

// --- COMPUTED ---
const allGroupedNewsImpacts = computed(() => {
  if (!newsImpactsStore.newsImpactsGroups.length || !newsImpactsStore.newsImpacts.length) {
    return [];
  }

  // Create a Set of news impact IDs that are associated with the current trade for efficient lookup.
  const tradeImpactIds = new Set(props.trade.news_impacts.map(impact => impact.id));

  const sortedGroups = [...newsImpactsStore.newsImpactsGroups].sort((a, b) => a.order - b.order);

  return sortedGroups.map(group => {
    // All possible impacts within this group.
    const impactsInGroup = newsImpactsStore.newsImpacts.filter(impact => impact.group_id === group.id);

    // Filter the impacts in this group to only include those associated with the trade.
    const tradeImpactsInGroup = impactsInGroup.filter(impact => tradeImpactIds.has(impact.id));

    return {
      ...group,
      impacts: impactsInGroup, // For the popover to select from.
      tradeImpacts: tradeImpactsInGroup, // For display.
    };
  });
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

// --- ADD IMPACT LOGIC ---
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
    selectedImpactIdsInPopover.value = group.tradeImpacts.map(t => t.id);
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
  const otherGroupImpactIds = props.trade.news_impacts.filter(impact => impact.group_id !== activeGroup.value.id).map(impact => impact.id);
  const finalImpactIds = [...otherGroupImpactIds, ...selectedImpactIdsInPopover.value];
  await tradesStore.updateTradeNewsImpacts(props.trade.id, finalImpactIds);
  isPopoverOpen.value = false;
  activeGroup.value = null;
};

const handleCancel = () => {
  isPopoverOpen.value = false;
  activeGroup.value = null;
};

// --- REMOVE IMPACT LOGIC ---
const enterDeleteMode = (groupId) => {
  if (isPopoverOpen.value) return;
  deletingFromGroupId.value = groupId;
};

const exitDeleteMode = () => {
  deletingFromGroupId.value = null;
};

const removeImpact = async (impactToRemove) => {
  const currentImpactIds = props.trade.news_impacts.map(t => t.id);
  const finalImpactIds = currentImpactIds.filter(id => id !== impactToRemove.id);
  await tradesStore.updateTradeNewsImpacts(props.trade.id, finalImpactIds);

  const remainingImpacts = props.trade.news_impacts.filter(t => t.group_id === impactToRemove.group_id && t.id !== impactToRemove.id);
  if (remainingImpacts.length === 0) {
    exitDeleteMode();
  }
};
</script>

<template>
  <div class="news-impact-manager-section">
    <div v-for="group in allGroupedNewsImpacts" :key="group.id" class="news-impact-group-row">
      <span class="group-name">{{ group.name }}</span>
      <div class="impacts-container">
        <div class="impact-pills-display">
            <div
                v-for="impact in group.tradeImpacts"
                :key="impact.id"
                class="impact-pill-wrapper"
                @click.stop="enterDeleteMode(group.id)"
            >
                <BasePill :style="{ backgroundColor: impact.color, color: getTextColor(impact.color) }" class="impact-pill">
                  {{ impact.name }}
                </BasePill>
                <button v-if="deletingFromGroupId === group.id" class="delete-impact-btn" @click.stop="removeImpact(impact)">
                    <CloseIcon />
                </button>
            </div>
            <p v-if="group.tradeImpacts.length === 0" class="no-impacts-message">-</p>
        </div>

        <IconButton v-if="deletingFromGroupId !== group.id" @click="openPopover($event, group)">
            <PlusIcon/>
        </IconButton>
        <BaseButton v-else variant="secondary" size="small" @click.stop="exitDeleteMode">Done</BaseButton>

      </div>
    </div>

    <div v-if="isPopoverOpen && activeGroup" :style="popoverStyle" class="popover-panel" ref="popoverRef">
        <div class="popover-content">
            <div class="impact-selection-list">
                <p v-if="activeGroup.impacts.length === 0" class="no-impacts-message">No impacts in this group.</p>
                <BaseCheckbox
                    v-for="impact in activeGroup.impacts"
                    :key="impact.id"
                    :value="impact.id"
                    v-model="selectedImpactIdsInPopover"
                >
                    {{ impact.name }}
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
.news-impact-manager-section {
  display: flex;
  flex-direction: column;

}
.news-impact-group-row {
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
.impacts-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.impact-pills-display {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
  align-items: center;
}
.no-impacts-message {
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
.impact-selection-list {
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
.impact-pill-wrapper {
  position: relative;
  display: inline-block;
  .impact-pill {
    cursor: pointer;
  }
}
.delete-impact-btn {
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