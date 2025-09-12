<script setup>
defineEmits(['close']);
</script>

<template>
  <div class="stat-selector-menu">
    <h4 class="menu-title">Customize Widgets</h4>
    <p class="wip-message">
      This feature is currently under development. Soon you will be able to add, remove, and reorder widgets here.
    </p>
    <button @click="$emit('close')" class="close-button">Close</button>
  </div>
</template>

<style scoped>
.stat-selector-menu {
  padding: 1rem;
  min-width: 250px;
}
.menu-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
.wip-message {
  font-size: 0.9rem;
  color: #6b7280; /* gray-500 */
  margin-bottom: 1rem;
}
.close-button {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e5e7eb; /* gray-200 */
  background-color: #f9fafb; /* gray-50 */
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s;
}
.close-button:hover {
  background-color: #f3f4f6; /* gray-100 */
}
</style>
