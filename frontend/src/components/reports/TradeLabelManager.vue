<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useLabelsStore } from '@/stores/labelsStore';
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
  labelType: { // es. 'mistakes', 'psychology-states', 'news-impacts'
    type: String,
    required: true,
  },
  title: { // es. 'Mistakes', 'Psychology', 'News Impact'
    type: String,
    required: true,
  }
});

const labelsStore = useLabelsStore();
const tradesStore = useTradesStore();

// --- STATE ---
const popoverRef = ref(null);
const isPopoverOpen = ref(false);
const popoverStyle = ref({});
const selectedIdsInPopover = ref([]);
const isDeleting = ref(false);

// --- DYNAMIC KEYS ---
const tradeLabelsKey = computed(() => props.labelType.replace(/-/g, '_'));

// --- LIFECYCLE ---
onMounted(() => {
  labelsStore.fetchLabelsIfNeeded(props.labelType);
});

onClickOutside(popoverRef, () => {
    if (isPopoverOpen.value) {
        isPopoverOpen.value = false;
    }
});

// --- COMPUTED ---
const allLabels = computed(() => labelsStore.labels[props.labelType] || []);
const tradeLabels = computed(() => props.trade[tradeLabelsKey.value] || []);

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

const openPopover = async (event) => {
    if (isDeleting.value) return;

    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();

    if (isPopoverOpen.value) {
        isPopoverOpen.value = false;
        return;
    }

    await nextTick();

    selectedIdsInPopover.value = tradeLabels.value.map(l => l.id);
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
  // La funzione in tradesStore si aspetta il labelType con i trattini
  await tradesStore._updateTradeLabels(props.trade.id, props.labelType, selectedIdsInPopover.value);
  isPopoverOpen.value = false;
};

const handleCancel = () => {
  isPopoverOpen.value = false;
};

// --- REMOVE LOGIC ---
const enterDeleteMode = () => {
  if (isPopoverOpen.value) return;
  isDeleting.value = true;
};

const exitDeleteMode = () => {
  isDeleting.value = false;
};

const removeItem = async (itemToRemove) => {
  const currentIds = tradeLabels.value.map(t => t.id);
  const finalIds = currentIds.filter(id => id !== itemToRemove.id);
  await tradesStore._updateTradeLabels(props.trade.id, props.labelType, finalIds);

  if (tradeLabels.value.length === 0) {
    exitDeleteMode();
  }
};
</script>

<template>
  <div class="manager-section">
    <div class="manager-row">
      <span class="manager-name">{{ title }}</span>
      <div class="items-container">
        <div class="item-pills-display">
            <div
                v-for="item in tradeLabels"
                :key="item.id"
                class="item-pill-wrapper"
                @click.stop="enterDeleteMode"
            >
                <BasePill :style="{ backgroundColor: item.color, color: getTextColor(item.color) }">
                  {{ item.name }}
                </BasePill>
                <button v-if="isDeleting" class="delete-item-btn" @click.stop="removeItem(item)">
                    <CloseIcon />
                </button>
            </div>
            <p v-if="tradeLabels.length === 0" class="no-items-message">-</p>
        </div>

        <IconButton v-if="!isDeleting" @click="openPopover($event)">
            <PlusIcon/>
        </IconButton>
        <BaseButton v-else variant="secondary" size="small" @click.stop="exitDeleteMode">Done</BaseButton>
      </div>
    </div>

    <div v-if="isPopoverOpen" :style="popoverStyle" class="popover-panel" ref="popoverRef">
        <div class="popover-content">
            <div class="item-selection-list">
                <p v-if="allLabels.length === 0" class="no-items-message">No {{ title.toLowerCase() }} available.</p>
                <BaseCheckbox
                    v-for="item in allLabels"
                    :key="item.id"
                    :value="item.id"
                    v-model="selectedIdsInPopover"
                >
                    {{ item.name }}
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
.manager-section {
  display: flex;
  flex-direction: column;
}
.manager-row {
  display: grid;
  grid-template-columns: 40% 1fr;
  gap: var(--semantic-size-stack-md);
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}
.manager-name {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  justify-self: start;
}
.items-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.item-pills-display {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
  align-items: center;
}
.no-items-message {
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
.item-selection-list {
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
.item-pill-wrapper {
  position: relative;
  display: inline-block;
  .item-pill {
    cursor: pointer;
  }
}
.delete-item-btn {
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