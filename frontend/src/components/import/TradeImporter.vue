<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/auth'; // Assuming you have this
import { useTradingAccountsStore } from '@/stores/tradingAccounts'; // Assuming you have this
import api from '@/services/api'; // Your API service
import brokerService from '@/services/brokerService';
import BaseButton from '@/components/ui/BaseButton.vue';

const uiStore = useUiStore();
const files = ref([]);
const uploadProgress = ref(0);
const isUploading = ref(false);
const importResult = ref(null);
const platforms = ref([]);
const selectedPlatform = ref(null);

// This should be passed as a prop or fetched from a store
const tradingAccountsStore = useTradingAccountsStore();
const selectedAccountId = computed(() => tradingAccountsStore.selectedTradingAccount?.id);


onMounted(async () => {
  try {
    const response = await brokerService.getPlatforms();
    platforms.value = response.data;
  } catch (error) {
    uiStore.showNotification({ message: 'Failed to load platforms.', type: 'error' });
  }
});

const onFileChange = (event) => {
  files.value = [...event.target.files];
};

const handleUpload = async () => {
  console.log('Attempting to upload...', {
    fileCount: files.value.length,
    accountId: selectedAccountId.value,
  });

  if (!files.value.length || !selectedAccountId.value || !selectedPlatform.value) {
    uiStore.showNotification({ message: 'Please select a trading account, a platform, and a file.', type: 'error' });
    return;
  }

  isUploading.value = true;
  importResult.value = null;

  const firstFile = files.value[0];
  const formData = new FormData();
  let endpoint = '';

  if (selectedPlatform.value === 'MT5') {
    if (!firstFile.name.toLowerCase().endsWith('.html')) {
      uiStore.showNotification({ message: 'For MT5, please upload an HTML file.', type: 'error' });
      isUploading.value = false;
      return;
    }
    if (files.value.length > 1) {
       uiStore.showNotification({ message: 'For MT5 import, only the first selected HTML file will be processed.', type: 'warning' });
    }
    formData.append('file', firstFile);
    endpoint = `/import/mt5/${selectedAccountId.value}`;
  } else if (selectedPlatform.value === 'Tradovate') {
    if (!firstFile.name.toLowerCase().endsWith('.csv')) {
      uiStore.showNotification({ message: 'For Tradovate, please upload a CSV file.', type: 'error' });
      isUploading.value = false;
      return;
    }
    files.value.forEach(file => {
      formData.append('files', file);
    });
    endpoint = `/import/tradovate/${selectedAccountId.value}`;
  } else {
    uiStore.showNotification({ message: 'Selected platform does not support import yet.', type: 'error' });
    isUploading.value = false;
    return;
  }

  try {
    const response = await api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      },
    });

    uiStore.showNotification({ message: 'File uploaded! Processing has started in the background.', type: 'info' });
    importResult.value = response.data; // Initial import run data
    pollImportStatus(response.data.id);

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred during upload.';
    uiStore.showNotification({ message: `Upload failed: ${errorMessage}`, type: 'error' });
  } finally {
    isUploading.value = false;
    uploadProgress.value = 0;
  }
};

const pollImportStatus = (importRunId) => {
  const interval = setInterval(async () => {
    try {
      const response = await api.get(`/import/status/${importRunId}`);
      importResult.value = response.data;
      if (response.data.status === 'applied' || response.data.status === 'failed') {
        clearInterval(interval);
      }
    } catch (error) {
      console.error('Failed to poll import status:', error);
      clearInterval(interval);
    }
  }, 3000); // Poll every 3 seconds
};
</script>

<template>
  <div class="trade-importer">
    <!-- Step 2: Select a Platform -->
    <div class="platform-selection-section">
      <label for="platform-select">Step 2: Select a Platform</label>
      <select id="platform-select" v-model="selectedPlatform">
        <option :value="null" disabled>-- Please choose a platform --</option>
        <option v-for="platform in platforms" :key="platform.id" :value="platform.name">
          {{ platform.name }}
        </option>
      </select>
    </div>

    <!-- Step 3: Upload Your File (Conditional) -->
    <div v-if="selectedPlatform === 'MT5' || selectedPlatform === 'Tradovate'">
      <div class="file-input-section">
        <label for="file-upload" class="file-upload-label">
          <span>Step 3: Upload Your File</span>
          <p v-if="selectedPlatform === 'MT5'">Only .html files are accepted.</p>
          <p v-if="selectedPlatform === 'Tradovate'">Only .csv files are accepted.</p>
        </label>
        <input
          id="file-upload"
          type="file"
          multiple
          @change="onFileChange"
          :accept="selectedPlatform === 'MT5' ? '.html' : '.csv'"
          :disabled="isUploading"
        />
        <div v-if="files.length" class="file-list">
          <p>Selected files:</p>
          <ul>
            <li v-for="file in files" :key="file.name">{{ file.name }}</li>
          </ul>
        </div>
      </div>
    </div>
    <div v-else-if="selectedPlatform">
      <p>Parser coming soon for {{ selectedPlatform }}.</p>
    </div>

    <BaseButton
      @click="handleUpload"
      :disabled="isUploading || !files.length || (selectedPlatform && !['MT5', 'Tradovate'].includes(selectedPlatform))"
    >
      {{ isUploading ? 'Uploading...' : 'Upload and Import' }}
    </BaseButton>

    <div v-if="isUploading" class="progress-bar-container">
      <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
    </div>

    <div v-if="importResult" class="import-result">
      <h3>Import Status</h3>
      <p><strong>Run ID:</strong> {{ importResult.id }}</p>
      <p><strong>Status:</strong> {{ importResult.status }}</p>
      <p v-if="importResult.status === 'applied'">
        Successfully processed! Inserted: {{ importResult.inserted_count }}, Updated: {{ importResult.updated_count }}, Skipped: {{ importResult.skipped_count }}.
      </p>
      <p v-if="importResult.error_message">
        <strong>Error:</strong> {{ importResult.error_message }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.trade-importer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.file-upload-label {
  border: 2px dashed #ccc;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  display: block;
}
input[type="file"] {
  display: none;
}
.progress-bar-container {
  width: 100%;
  background-color: #f3f3f3;
  border-radius: 5px;
}
.progress-bar {
  height: 20px;
  background-color: #4caf50;
  border-radius: 5px;
  transition: width 0.4s ease;
}
.import-result {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
}
</style>