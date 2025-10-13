<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useImageStore } from '../../stores/imageStore';
import { storeToRefs } from 'pinia';
import { DocumentArrowUpIcon, PencilIcon, TrashIcon, ArrowDownOnSquareIcon, MagnifyingGlassPlusIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  tradeId: {
    type: String,
    required: true,
  },
  mode: {
    type: String,
    default: 'full', // 'full', 'gallery-only', 'uploader-only'
    validator: (value) => ['full', 'gallery-only', 'uploader-only'].includes(value),
  },
  images: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['insert-image', 'edit-image', 'open-lightbox']);

const imageStore = useImageStore();
const { imagesForCurrentTrade: imagesFromStore, isLoading } = storeToRefs(imageStore);

const isDragging = ref(false);

const imagesForCurrentTrade = computed(() => {
  return props.mode === 'full' ? imagesFromStore.value : props.images;
});

onMounted(() => {
  if (props.mode === 'full') {
    imageStore.fetchImagesForTrade(props.tradeId);
  }
});

watch(() => props.tradeId, (newTradeId) => {
  if (props.mode === 'full') {
    imageStore.fetchImagesForTrade(newTradeId);
  }
});

const handleFileDrop = (event) => {
  isDragging.value = false;
  const files = event.dataTransfer.files;
  if (files.length) {
    handleFileUpload(files[0]);
  }
};

const handleFileSelect = (event) => {
  const files = event.target.files;
  if (files.length) {
    handleFileUpload(files[0]);
  }
};

const handleFileUpload = (file) => {
  imageStore.uploadImage(props.tradeId, file);
};

const onInsert = (imageUrl) => {
  emit('insert-image', imageUrl);
};

const onEdit = (image) => {
  emit('edit-image', image);
};

const onDelete = async (imageId) => {
  if (confirm('Are you sure you want to delete this image? This cannot be undone.')) {
    await imageStore.deleteImage(imageId);
  }
};
</script>

<template>
  <div class="trade-image-gallery">
    <!-- Uploader Section -->
    <div
      v-if="mode === 'full' || mode === 'uploader-only'"
      class="upload-area"
      :class="{ 'is-dragging': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleFileDrop"
      @click="() => $refs.fileInput.click()"
    >
      <DocumentArrowUpIcon class="upload-icon" />
      <p>Drop an image here or click to upload</p>
      <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" class="hidden-input" />
    </div>

    <!-- Gallery Section -->
    <div v-if="mode === 'full' || mode === 'gallery-only'">
      <div v-if="isLoading" class="loading-spinner">Loading images...</div>

      <div v-else-if="imagesForCurrentTrade.length === 0" class="empty-state">
        <p>No images have been attached to this trade yet.</p>
      </div>

      <div class="image-grid" v-else>
        <div v-for="(image, index) in imagesForCurrentTrade" :key="image.id" class="image-card" @click="emit('open-lightbox', index)">
          <img :src="image.url" :alt="image.description || 'Trade image'" class="thumbnail" />
          <div class="image-overlay">
            <div class="image-actions">
              <button v-if="mode === 'full'" @click.stop="onInsert(image.url)" class="action-btn" title="Insert into Note">
                <ArrowDownOnSquareIcon />
              </button>
              <button @click.stop="onEdit(image)" class="action-btn" title="Edit Details">
                <PencilIcon />
              </button>
              <button @click.stop="onDelete(image.id)" class="action-btn danger" title="Delete Image">
                <TrashIcon />
              </button>
            </div>
            <div class="zoom-indicator">
              <MagnifyingGlassPlusIcon />
            </div>
            <p class="image-description">{{ image.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.trade-image-gallery {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.upload-area {
  border: 2px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  color: var(--semantic-color-text-secondary);

  &:hover, &.is-dragging {
    background-color: var(--semantic-color-surface-tertiary);
    border-color: var(--semantic-color-border-focus);
  }

  .upload-icon {
    width: 3rem;
    height: 3rem;
    margin: 0 auto 0.5rem;
    color: var(--semantic-color-text-disabled);
  }
}

.hidden-input {
  display: none;
}

.loading-spinner, .empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--semantic-color-text-secondary);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-card {
  position: relative;
  overflow: hidden;
  border-radius: var(--semantic-border-radius-interactive);
  aspect-ratio: 1 / 1;
  cursor: pointer;

  .thumbnail {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .image-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 50%);
    opacity: 0;
    transition: opacity 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0.75rem;
    color: white;
  }

  &:hover .image-overlay {
    opacity: 1;
  }
  &:hover .thumbnail {
    transform: scale(1.05);
  }
}

.image-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;

  svg {
    width: 16px;
    height: 16px;
  }

  &:hover {
    background-color: rgba(255, 255, 255, 0.4);
  }

  &.danger:hover {
    background-color: var(--semantic-color-feedback-negative-bg-default);
    color: var(--semantic-color-feedback-negative-text);
  }
}

.image-description {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: auto;
}

.zoom-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  width: 48px;
  height: 48px;
  opacity: 0;
  transition: opacity 0.3s ease;

  .image-card:hover & {
    opacity: 0.8;
  }
}
</style>