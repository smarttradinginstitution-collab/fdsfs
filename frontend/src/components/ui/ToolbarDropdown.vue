<template>
  <div class="toolbar-dropdown" ref="dropdownRef">
    <button @click="toggleDropdown" class="dropdown-toggle">
      <slot name="button"></slot>
      <span class="arrow">&#9662;</span>
    </button>
    <div v-if="isOpen" class="dropdown-menu">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { onClickOutside } from '@vueuse/core';

const isOpen = ref(false);
const dropdownRef = ref(null);

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

onClickOutside(dropdownRef, () => {
  isOpen.value = false;
});
</script>

<style scoped>
.toolbar-dropdown {
  position: relative;
  display: inline-block;
}
.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
.dropdown-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.arrow {
  font-size: 0.6rem;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #2d3748; /* gray-800 */
  border: 1px solid #4a5568; /* gray-600 */
  border-radius: 4px;
  padding: 0.5rem;
  z-index: 10;
  min-width: 100px;
}
</style>
