import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { ref } from 'vue';
import { useUiStore } from './uiStore';

export const useImageStore = defineStore('imageStore', () => {
  const imagesForCurrentTrade = ref([]);
  const isLoading = ref(false);
  const uiStore = useUiStore();

  async function fetchImagesForTrade(tradeId) {
    if (!tradeId) {
      imagesForCurrentTrade.value = [];
      return [];
    }
    isLoading.value = true;
    try {
      const response = await apiClient.get(`/trades/${tradeId}/images`);
      imagesForCurrentTrade.value = response.data;
      return response.data; // Restituisce i dati delle immagini
    } catch (error) {
      console.error('Error fetching images for trade:', error);
      uiStore.showNotification({ message: 'Failed to load trade images.', type: 'error' });
      imagesForCurrentTrade.value = [];
      return []; // Restituisce un array vuoto in caso di errore
    } finally {
      isLoading.value = false;
    }
  }

  async function uploadImage(tradeId, file, metadata = {}) {
    if (!tradeId || !file) return;

    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      if (metadata[key] !== null && metadata[key] !== undefined) {
        formData.append(key, metadata[key]);
      }
    });

    uiStore.showNotification({ message: 'Uploading image...', type: 'loading' });
    try {
      const response = await apiClient.post(`/trades/${tradeId}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      imagesForCurrentTrade.value.push(response.data);
      uiStore.showNotification({ message: 'Image uploaded successfully!', type: 'success' });
    } catch (error) {
      console.error('Error uploading image:', error);
      uiStore.showNotification({ message: 'Image upload failed.', type: 'error' });
    }
  }

  async function updateImageMetadata(imageId, metadata) {
    if (!imageId) return;
    try {
      const response = await apiClient.patch(`/images/${imageId}`, metadata);
      const index = imagesForCurrentTrade.value.findIndex(img => img.id === imageId);
      if (index !== -1) {
        imagesForCurrentTrade.value[index] = response.data;
      }
      uiStore.showNotification({ message: 'Image details updated.', type: 'success' });
    } catch (error) {
      console.error('Error updating image metadata:', error);
      uiStore.showNotification({ message: 'Failed to update image details.', type: 'error' });
    }
  }

  async function deleteImage(imageId) {
    if (!imageId) return;
    try {
      await apiClient.delete(`/images/${imageId}`);
      imagesForCurrentTrade.value = imagesForCurrentTrade.value.filter(img => img.id !== imageId);
      uiStore.showNotification({ message: 'Image deleted.', type: 'success' });
    } catch (error) {
      console.error('Error deleting image:', error);
      uiStore.showNotification({ message: 'Failed to delete image.', type: 'error' });
    }
  }

  return {
    imagesForCurrentTrade,
    isLoading,
    fetchImagesForTrade,
    uploadImage,
    updateImageMetadata,
    deleteImage,
  };
});