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
const icons = import.meta.glob('../../assets/icons/*.svg', { as: 'raw' });

async function loadIcon() {
  const iconPath = `../../assets/icons/${props.name}.svg`;
  if (icons[iconPath]) {
    icon.value = await icons[iconPath]();
  } else {
    console.error(`Icon not found: ${props.name}`);
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
