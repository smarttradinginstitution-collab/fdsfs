<template>
  <div class="color-picker">
    <input type="color" :value="color" @input="onInput" class="color-input" />
  </div>
</template>

<script setup>
const props = defineProps({
  color: {
    type: String,
    default: '#ffffff',
  },
});

const emit = defineEmits(['update:color']);

const onInput = (event) => {
  emit('update:color', event.target.value);
};
</script>

<style scoped>
.color-picker {
  display: inline-block;
}
.color-input {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}
/* Hide the color input's native text/hex value display */
.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}
.color-input::-webkit-color-swatch {
  border: 1px solid #4a5568; /* gray-600 */
  border-radius: 4px;
}
</style>
