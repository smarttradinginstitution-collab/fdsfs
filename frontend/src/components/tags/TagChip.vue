<script setup>
import { computed } from "vue";
import { hexToRgba } from "@/services/colorUtils";
import PencilIcon from "@/components/icons/PencilIcon.vue";
import TrashIcon from "@/components/icons/TrashIcon.vue";

const props = defineProps({
  tag: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['edit', 'delete']);

const chipStyle = computed(() => {
  const backgroundColor = props.tag.color || "#cccccc"; // Default gray
  return {
    backgroundColor: hexToRgba(backgroundColor, 0.2),
    color: backgroundColor,
    border: `1px solid ${backgroundColor}`,
  };
});
</script>

<template>
  <div class="tag-chip" :style="chipStyle">
    <span>{{ tag.name_tag }}</span>
    <div class="actions">
      <button class="action-btn" @click.stop="emit('edit', tag)">
        <PencilIcon :style="{ color: chipStyle.color }" />
      </button>
      <button class="action-btn" @click.stop="emit('delete', tag)">
        <TrashIcon :style="{ color: chipStyle.color }" />
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px 4px 12px;
  border-radius: var(--semantic-border-radius-pill);
  font: var(--semantic-font-style-label-sm);
  font-weight: var(--base-font-weight-medium);
  white-space: nowrap;
  cursor: default;
  transition: padding 0.2s ease;

  .actions {
    display: none; // Hidden by default
    align-items: center;
    gap: 4px;
  }

  .action-btn {
     background: none;
    border: none;
    padding: 0;
    margin: 0;
    cursor: pointer;
    line-height: 0;

    svg {
      width: 12px;
      height: 12px;
      transition: transform 0.2s ease;
    }

    &:hover svg {
      transform: scale(1.2);
    }
  }

  &:hover {
    padding-right: 12px;
    .actions {
      display: inline-flex; // Show on hover
    }
  }
}
</style>