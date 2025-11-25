<template>
  <div
    class="gallery-editor-container p-4 border border-gray-700 rounded-lg bg-gray-800/50"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    :class="{ 'border-blue-500 bg-gray-700/50': isDragging }"
  >
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Uploading image...</p>
    </div>

    <!-- Area di Upload -->
    <div class="upload-area text-center p-3 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:border-blue-400 transition-colors" @click="triggerFileInput">
      <input type="file" ref="fileInput" @change="onFileSelect" class="hidden" accept="image/*" />
      <div class="text-gray-400 flex flex-col items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="mt-2 text-xs">Trascina un'immagine o <span class="font-semibold text-blue-400">clicca per caricare</span></p>
      </div>
    </div>

    <!-- Griglia Immagini -->
    <div v-if="content.images && content.images.length" class="image-grid mt-4 grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
      <div v-for="(image, index) in content.images" :key="image.id" class="relative group rounded-lg overflow-hidden cursor-pointer" @click="openImage(index)">
        <img :src="image.url" :alt="image.description || 'Gallery image'" class="w-24 h-24 object-cover transition-transform duration-300 group-hover:scale-105">
        <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all flex flex-col items-center justify-center">
          <!-- Zoom Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
          </svg>
          <!-- Delete Button -->
          <button @click.stop="removeImage(image.id)" class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 bg-red-600/80 rounded-full hover:bg-red-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    <div v-else class="text-center mt-6 text-gray-500">
      <p>Nessuna immagine ancora caricata.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useRoute } from 'vue-router';

const props = defineProps({
  content: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:content', 'open-lightbox']);

const playbookStore = usePlaybookStore();
const route = useRoute();
const playbookId = route.params.id;

const fileInput = ref(null);
const isDragging = ref(false);
const isLoading = ref(false);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const onDragOver = () => { isDragging.value = true; };
const onDragLeave = () => { isDragging.value = false; };

const onDrop = (event) => {
  isDragging.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0 && files[0].type.startsWith('image/')) {
    handleFileUpload(files[0]);
  }
};

const onFileSelect = (event) => {
  const files = event.target.files;
  if (files.length > 0) {
    handleFileUpload(files[0]);
  }
};

const handleFileUpload = async (file) => {
  isLoading.value = true;
  try {
    const newImage = await playbookStore.uploadPlaybookImage({
      playbookId: playbookId,
      file: file,
    });

    const updatedImages = [...(props.content.images || []), newImage];
    emit('update:content', { ...props.content, images: updatedImages });

  } catch (error) {
    console.error("Upload failed:", error);
    // TODO: Aggiungere notifica all'utente
  } finally {
    isLoading.value = false;
  }
};

const removeImage = (imageId) => {
  const updatedImages = props.content.images.filter(img => img.id !== imageId);
  emit('update:content', { ...props.content, images: updatedImages });
  // TODO: Aggiungere chiamata API per eliminare l'immagine dal backend e da Supabase
  console.log("Removing image locally:", imageId);
};

const openImage = (index) => {
  emit('open-lightbox', {
    images: props.content.images,
    startIndex: index,
  });
};
</script>

<style scoped>
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid #3b82f6;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(17, 24, 39, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 0.5rem;
  color: white;
}
</style>
