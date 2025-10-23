<template>
  <p class="advice-text">
    <slot>{{ text }}</slot>
  </p>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.advice-text {
  font-size: 0.875rem;
  color: #a0aec0; /* Cool Gray 400 */
  line-height: 1.5;
}
</style>
