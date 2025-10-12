<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { ArrowLongRightIcon, ChatBubbleBottomCenterTextIcon, TrashIcon, HandRaisedIcon, PencilIcon as PencilSolidIcon } from '@heroicons/vue/24/solid';
import { RectangleStackIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  imageUrl: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['save', 'cancel']);

const canvasEl = ref(null);
let canvas = null;

const activeTool = ref('pan');
const strokeColor = ref('#ff0000');

const initializeCanvas = () => {
  if (canvas) {
    canvas.dispose();
  }

  const fabric = window.fabric; // Use the globally available fabric object
  if (!fabric) {
    console.error("Fabric.js not loaded from CDN!");
    alert("Error: Annotation library could not be loaded. Please check your internet connection and try again.");
    return;
  }

  canvas = new fabric.Canvas(canvasEl.value, {
    isDrawingMode: false,
  });

  fabric.Image.fromURL(props.imageUrl, (img) => {
    const container = canvasEl.value.parentElement;
    if (!container) return;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    const scale = Math.min(containerWidth / img.width, containerHeight / img.height, 1);

    canvas.setWidth(img.width * scale);
    canvas.setHeight(img.height * scale);

    canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas), {
      scaleX: scale,
      scaleY: scale,
    });
  }, { crossOrigin: 'anonymous' });
};

const setTool = (tool) => {
  if (!canvas) return;
  activeTool.value = tool;
  canvas.isDrawingMode = tool === 'draw';
  canvas.selection = tool === 'pan';
  canvas.defaultCursor = tool === 'pan' ? 'grab' : 'crosshair';
  canvas.getObjects().forEach(o => o.set({ selectable: tool === 'pan' }));
  canvas.renderAll();
};

const addRect = () => {
    if (!canvas) return;
    const rect = new window.fabric.Rect({
        left: 100, top: 100, fill: 'transparent', stroke: strokeColor.value,
        strokeWidth: 2, width: 200, height: 100,
    });
    canvas.add(rect);
    setTool('pan');
};

const addArrow = () => {
    if (!canvas) return;
    const fabric = window.fabric;
    const line = new fabric.Line([50, 100, 250, 100], { stroke: strokeColor.value, strokeWidth: 2 });
    const arrowHead = new fabric.Triangle({
        left: 250, top: 100, width: 10, height: 10, fill: strokeColor.value,
        angle: 90, originX: 'center', originY: 'center',
    });
    const arrow = new fabric.Group([line, arrowHead], { left: 50, top: 100 });
    canvas.add(arrow);
    setTool('pan');
};

const addText = () => {
    if (!canvas) return;
    const text = new window.fabric.IText('Your Text', {
        left: 100, top: 150, fill: strokeColor.value, fontSize: 20,
    });
    canvas.add(text);
    text.enterEditing();
    text.selectAll();
    setTool('pan');
};

const deleteSelected = () => {
    if (!canvas) return;
    canvas.remove(...canvas.getActiveObjects());
    canvas.discardActiveObject().renderAll();
};

onMounted(() => {
    nextTick(() => {
        // A short delay to ensure the global fabric script has loaded
        setTimeout(() => {
            initializeCanvas();
        }, 100);
    });
});

onBeforeUnmount(() => {
  if (canvas) {
    canvas.dispose();
  }
});

watch(() => props.imageUrl, () => {
  initializeCanvas();
});

const saveImage = () => {
  if (!canvas) return;
  const dataUrl = canvas.toDataURL({ format: 'png' });
  emit('save', dataUrl);
};
</script>

<template>
  <div class="annotator-container">
    <div class="toolbar">
      <button @click="setTool('pan')" :class="{ 'is-active': activeTool === 'pan' }" title="Pan/Select"><HandRaisedIcon/></button>
      <button @click="setTool('draw')" :class="{ 'is-active': activeTool === 'draw' }" title="Draw"><PencilSolidIcon/></button>
      <div class="divider"></div>
      <button @click="addRect" title="Add Rectangle"><RectangleStackIcon/></button>
      <button @click="addArrow" title="Add Arrow"><ArrowLongRightIcon/></button>
      <button @click="addText" title="Add Text"><ChatBubbleBottomCenterTextIcon/></button>
      <div class="divider"></div>
      <input type="color" v-model="strokeColor" class="color-picker" title="Select Color" />
      <button @click="deleteSelected" title="Delete Selected"><TrashIcon/></button>
      <div class="divider"></div>
      <button @click="saveImage" class="action-save">Save</button>
      <button @click="$emit('cancel')" class="action-cancel">Cancel</button>
    </div>
    <div class="canvas-wrapper">
      <canvas ref="canvasEl"></canvas>
    </div>
  </div>
</template>

<style scoped lang="scss">
.annotator-container {
  position: fixed;
  inset: 0;
  background-color: rgba(24, 26, 32, 0.9);
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  color: white;
}

.toolbar {
  background-color: var(--semantic-color-surface-primary);
  padding: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid var(--semantic-color-border-default);
  flex-shrink: 0;

  button {
    background: none;
    border: 1px solid transparent;
    color: var(--semantic-color-text-secondary);
    padding: 0.5rem;
    border-radius: var(--semantic-border-radius-interactive);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 20px;
      height: 20px;
    }

    &:hover {
      background-color: var(--semantic-color-surface-secondary);
      color: var(--semantic-color-text-primary);
    }

    &.is-active {
      background-color: var(--semantic-color-surface-tertiary);
      color: var(--semantic-color-text-focus);
      border-color: var(--semantic-color-border-focus);
    }
  }

  .divider {
    width: 1px;
    height: 24px;
    background-color: var(--semantic-color-border-default);
    margin: 0 0.5rem;
  }

  .color-picker {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    width: 36px;
    height: 36px;
    border: none;
    cursor: pointer;
    background-color: transparent;
    padding: 0;
    border-radius: 50%;

    &::-webkit-color-swatch-wrapper {
      padding: 0;
      border-radius: 50%;
    }
    &::-webkit-color-swatch {
      border: 2px solid var(--semantic-color-border-default);
      border-radius: 50%;
    }
  }

  .action-save, .action-cancel {
    padding: 0.5rem 1rem;
    font-weight: 500;
  }
  .action-save {
    background-color: var(--semantic-color-action-primary-default);
    color: var(--semantic-color-action-primary-text);
    &:hover {
      background-color: var(--semantic-color-action-primary-hover);
    }
  }
}

.canvas-wrapper {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding: 2rem;
}

canvas {
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
</style>