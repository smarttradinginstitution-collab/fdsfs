<script setup>
import { ref } from 'vue';
import { NodeViewWrapper } from '@tiptap/vue-3';
import { ArrowsPointingOutIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  updateAttributes: {
    type: Function,
    required: true,
  },
  selected: {
    type: Boolean,
    required: true,
  },
});

const imgRef = ref(null);

const onMousedown = (e) => {
  e.preventDefault();
  e.stopPropagation();

  const initialWidth = imgRef.value.offsetWidth;
  const initialHeight = imgRef.value.offsetHeight;
  const aspectRatio = initialWidth / initialHeight;

  const onMousemove = (moveEvent) => {
    const newWidth = initialWidth + (moveEvent.clientX - e.clientX);
    imgRef.value.style.width = `${newWidth}px`;
    imgRef.value.style.height = `${newWidth / aspectRatio}px`; // Maintain aspect ratio
  };

  const onMouseup = () => {
    window.removeEventListener('mousemove', onMousemove);
    window.removeEventListener('mouseup', onMouseup);
    props.updateAttributes({
      width: imgRef.value.offsetWidth,
      height: imgRef.value.offsetHeight,
    });
  };

  window.addEventListener('mousemove', onMousemove);
  window.addEventListener('mouseup', onMouseup);
};
</script>

<template>
  <node-view-wrapper class="resizable-image-wrapper" :class="{ 'is-selected': selected }">
    <div v-if="selected" class="drag-handle" data-drag-handle>
      <ArrowsPointingOutIcon class="drag-icon" />
    </div>
    <img
      :src="node.attrs.src"
      :style="{
        width: node.attrs.width ? `${node.attrs.width}px` : null,
        height: node.attrs.height ? `${node.attrs.height}px` : null,
      }"
      ref="imgRef"
    />
    <div v-if="selected" class="resize-handle" @mousedown="onMousedown"></div>
  </node-view-wrapper>
</template>

<style scoped>
.resizable-image-wrapper {
  position: relative;
  display: inline-block;
  line-height: 0; /* Removes bottom space under the image */
}

.resizable-image-wrapper.is-selected {
  outline: 2px solid var(--semantic-color-border-focus);
}

img {
  display: block;
  max-width: 100%;
  height: auto;
}

.resize-handle {
  position: absolute;
  right: -5px;
  bottom: -5px;
  width: 10px;
  height: 10px;
  background-color: var(--semantic-color-border-focus);
  border: 1px solid white;
  border-radius: 50%;
  cursor: nwse-resize;
  display: none;
}

.resizable-image-wrapper.is-selected .resize-handle {
  display: block;
}

.drag-handle {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  cursor: grab;
  padding: 2px;
  display: none; /* Hidden by default */
}

.resizable-image-wrapper.is-selected .drag-handle {
  display: block;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-icon {
  width: 16px;
  height: 16px;
  color: white;
}
</style>