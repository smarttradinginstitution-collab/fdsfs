<script setup>
import { computed } from "vue";
import { hexToRgba } from "@/services/colorUtils"; // Assuming a color utility exists

const props = defineProps({
  tag: {
    type: Object,
    required: true,
  },
});

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
    {{ tag.name_tag }}
  </div>
</template>

<style lang="scss" scoped>
.tag-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--semantic-border-radius-pill);
  font: var(--semantic-font-style-label-sm);
  font-weight: var(--base-font-weight-medium);
  white-space: nowrap;
  cursor: default;
}
</style>