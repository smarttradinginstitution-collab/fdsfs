<script setup>
import { ref, computed, onUnmounted } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import api from '@/services/api';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  selectedPlatform: {
    type: String,
    default: null,
  },
});

const uiStore = useUiStore();
const files = ref([]);
const uploadProgress = ref(0);
const isUploading = ref(false);
const importResult = ref(null);
const pollingInterval = ref(null);
const tradingAccountsStore = useTradingAccountsStore();
const selectedAccountId = computed(() => tradingAccountsStore.selectedTradingAccount?.id);

const onFileChange = (event) => {
  files.value = [...event.target.files];
};

const handleUpload = async () => {
  if (!files.value.length || !selectedAccountId.value || !props.selectedPlatform) {
    uiStore.showNotification({ message: 'Please select a trading account, a platform, and a file.', type: 'error' });
    return;
  }

  isUploading.value = true;
  importResult.value = null;
  if (pollingInterval.value) clearInterval(pollingInterval.value);

  const file = files.value[0];
  const formData = new FormData();
  let endpoint = '';
  let platformKey = props.selectedPlatform.toLowerCase();

  // Validazione estensione file
  const allowedExtensions = {
    mt5: '.html',
    tradovate: '.csv',
    ninjatrader: '.csv',
  };
  const requiredExtension = allowedExtensions[platformKey];

  if (requiredExtension && !file.name.toLowerCase().endsWith(requiredExtension)) {
    uiStore.showNotification({ message: `For ${props.selectedPlatform}, please upload a ${requiredExtension} file.`, type: 'error' });
    isUploading.value = false;
    return;
  }

  formData.append('file', file);
  endpoint = `/import/${platformKey}/${selectedAccountId.value}`;

  try {
    const response = await api.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      },
    });

    importResult.value = response.data;

    // Check status immediately
    if (['applied', 'failed'].includes(response.data.status)) {
        const messageType = response.data.status === 'applied' ? 'success' : 'error';
        const message = response.data.status === 'applied' ? 'File already processed. Showing previous result.' : 'Import failed.';
        uiStore.showNotification({ message, type: messageType });
    } else {
        const message = 'File uploaded! Processing has started in the background.';
        uiStore.showNotification({ message, type: 'info' });
        pollImportStatus(response.data.id);
    }

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred during upload.';
    uiStore.showNotification({ message: `Upload failed: ${errorMessage}`, type: 'error' });
  } finally {
    isUploading.value = false;
    uploadProgress.value = 0;
  }
};

const pollImportStatus = (importRunId) => {
  pollingInterval.value = setInterval(async () => {
    try {
      const response = await api.get(`/import/status/${importRunId}`);
      importResult.value = response.data;

      if (['applied', 'failed'].includes(response.data.status)) {
        clearInterval(pollingInterval.value);
         if (response.data.status === 'failed') {
            uiStore.showNotification({ message: `Import failed: ${response.data.error_message}`, type: 'error' });
         } else {
            uiStore.showNotification({ message: 'Import completed successfully!', type: 'success' });
         }
      }
    } catch (error) {
      console.error('Failed to poll import status:', error);
      clearInterval(pollingInterval.value);
      uiStore.showNotification({
          message: 'Lost connection while checking import status.',
          type: 'error'
      });
    }
  }, 3000);
};

// Cleanup on component unmount
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
  }
});

const isUploadDisabled = computed(() => {
  return isUploading.value || !files.value.length || !props.selectedPlatform || !['MT5', 'Tradovate', 'NinjaTrader'].includes(props.selectedPlatform);
});
</script>

<template>
  <div class="trade-importer">
    <div v-if="props.selectedPlatform === 'MT5' || props.selectedPlatform === 'Tradovate' || props.selectedPlatform === 'NinjaTrader'">
      <div class="file-input-section">
        <label for="file-upload" class="file-upload-label">
          <p v-if="props.selectedPlatform === 'MT5'">Only .html files are accepted.</p>
          <p v-if="props.selectedPlatform === 'Tradovate' || props.selectedPlatform === 'NinjaTrader'">Only .csv files are accepted.</p>
        </label>
        <input id="file-upload" type="file" @change="onFileChange" :accept="props.selectedPlatform === 'MT5' ? '.html' : '.csv'" :disabled="isUploading" />

        <div v-if="files.length" class="file-list">
          <p>Selected file:</p>
          <ul>
            <li v-for="file in files" :key="file.name">{{ file.name }}</li>
          </ul>
        </div>
      </div>
    </div>
    <div v-else-if="props.selectedPlatform">
      <p>Parser coming soon for {{ props.selectedPlatform }}.</p>
    </div>

    <BaseButton @click="handleUpload" :disabled="isUploadDisabled">
      {{ isUploading ? 'Uploading...' : 'Upload and Import' }}
    </BaseButton>

    <div v-if="isUploading && uploadProgress > 0" class="progress-bar-container">
      <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
    </div>

    <div v-if="importResult" class="import-result">
      <h3>Import Status</h3>
      <p><strong>Run ID:</strong> {{ importResult.id }}</p>

      <!-- Enhanced Status Display -->
      <p>
        <strong>Status:</strong>
        <span :class="`status-${importResult.status}`">{{ importResult.status }}</span>
        <span v-if="['parsing', 'applying'].includes(importResult.status) && importResult.total_rows > 0">
           ({{ importResult.total_rows }} rows detected)
        </span>
      </p>

      <div v-if="importResult.status === 'applied'">
        <p>Successfully processed!</p>
        <p>Inserted: {{ importResult.inserted_count }}, Updated: {{ importResult.updated_count }}, Skipped: {{ importResult.skipped_count }}.</p>
      </div>

      <p v-if="importResult.error_message" class="error-message">
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
  overflow: hidden;
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

.status-applied {
  color: #4caf50;
  font-weight: bold;
}

.status-failed {
  color: #f44336;
  font-weight: bold;
}

.status-queued, .status-parsing, .status-applying {
    color: #2196F3;
    font-weight: bold;
}

.error-message {
  color: #f44336;
}
</style>
