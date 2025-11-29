<template>
  <div class="emoji-selector">
    <div class="selected-emoji" @click="togglePicker">
      {{ selectedEmoji || '&#x1f600;' }}
    </div>
    <div v-if="isPickerOpen" class="emoji-picker">
      <div
        v-for="emoji in emojis"
        :key="emoji"
        class="emoji-item"
        @click="selectEmoji(emoji)"
      >
        {{ emoji }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { onClickOutside } from '@vueuse/core';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['update:modelValue']);

const isPickerOpen = ref(false);
const selectedEmoji = ref(props.modelValue);
const selectorRef = ref(null);

const emojis = [
  '😀', '📈', '📉', '🧠', '💡', '🔥', '🎯', '🚀', '⭐', '🏆',
  '✅', '❌', '⚠️', '🔄', '🤔', '💪', '💰', '💸', '⏳', '🔔',
];

const togglePicker = () => {
  isPickerOpen.value = !isPickerOpen.value;
};

const selectEmoji = (emoji) => {
  selectedEmoji.value = emoji;
  emit('update:modelValue', emoji);
  isPickerOpen.value = false;
};

onClickOutside(selectorRef, () => {
  isPickerOpen.value = false;
});
</script>

<style scoped>
.emoji-selector {
  position: relative;
}
.selected-emoji {
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  background-color: #374151; /* gray-700 */
  display: inline-block;
}
.emoji-picker {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #2d3748; /* gray-800 */
  border: 1px solid #4a5568; /* gray-600 */
  border-radius: 8px;
  padding: 0.5rem;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  z-index: 20;
}
.emoji-item {
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.25rem;
  border-radius: 4px;
  text-align: center;
}
.emoji-item:hover {
  background-color: #4a5568; /* gray-600 */
}
</style>
