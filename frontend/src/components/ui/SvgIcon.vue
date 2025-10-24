<template>
  <div v-if="icon" class="svg-icon" v-html="icon"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  size: {
    type: [Number, String],
    default: 24,
  },
  strokeWidth: {
    type: [Number, String],
    default: 2,
  },
});

const icon = ref(null);

async function loadIcon() {
  try {
    const iconModule = await import(`../../assets/icons/${props.name}.svg?raw`);
    icon.value = iconModule.default;
  } catch (e) {
    console.error(`Could not load icon: ${props.name}`, e);
    icon.value = null;
  }
}

onMounted(loadIcon);
watch(() => props.name, loadIcon);
</script>

<style scoped>
.svg-icon {
  display: inline-block;
  width: v-bind(size + 'px');
  height: v-bind(size + 'px');
}
.svg-icon :deep(svg) {
  width: 100%;
  height: 100%;
  stroke-width: v-bind(strokeWidth);
  stroke: currentColor;
}
</style>
