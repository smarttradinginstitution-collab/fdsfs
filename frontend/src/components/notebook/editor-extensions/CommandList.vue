<template>
  <div class="items-container">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="item"
      :class="{ 'is-selected': selectedIndex === index }"
      @click="selectItem(index)"
    >
      {{ item.title }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  command: {
    type: Function,
    required: true,
  },
});

const selectedIndex = ref(0);

const selectItem = (index) => {
  const item = props.items[index];
  if (item) {
    props.command(item);
  }
};

const onKeyDown = ({ event }) => {
  if (event.key === 'ArrowUp') {
    upHandler();
    return true;
  }
  if (event.key === 'ArrowDown') {
    downHandler();
    return true;
  }
  if (event.key === 'Enter') {
    enterHandler();
    return true;
  }
  return false;
};

const upHandler = () => {
  selectedIndex.value = (selectedIndex.value + props.items.length - 1) % props.items.length;
};

const downHandler = () => {
  selectedIndex.value = (selectedIndex.value + 1) % props.items.length;
};

const enterHandler = () => {
  selectItem(selectedIndex.value);
};

watch(() => props.items, () => {
  selectedIndex.value = 0;
});

defineExpose({
  onKeyDown,
});
</script>

<style lang="scss" scoped>
.items-container {
  padding: 0.2rem;
  position: relative;
  border-radius: 0.5rem;
  background: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
  overflow: hidden;
  font-size: 0.9rem;
  box-shadow: 0 0 0 1px var(--semantic-color-border-default), 0px 10px 20px rgba(0, 0, 0, 0.1);
}

.item {
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  border-radius: 0.4rem;
  border: 1px solid transparent;
  padding: 0.2rem 0.4rem;
  cursor: pointer;

  &.is-selected {
    border-color: var(--semantic-color-border-default);
    background-color: var(--semantic-color-surface-secondary);
  }
}
</style>