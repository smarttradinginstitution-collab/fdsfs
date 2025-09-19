<script setup>
import { ref, computed } from 'vue';
import BaseModal from '../ui/BaseModal.vue';
import BaseButton from '../ui/BaseButton.vue';
import UploadIcon from '../icons/UploadIcon.vue';

const emit = defineEmits(['close', 'submit-import']);
const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  importSummary: {
    type: Object,
    default: null,
  },
});

const selectedFile = ref(null);
const fileInput = ref(null);

const fileName = computed(() => selectedFile.value?.name || 'Nessun file selezionato');

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file && file.type === 'text/csv') {
    selectedFile.value = file;
  } else {
    selectedFile.value = null;
    // Potremmo mostrare una notifica di errore qui
    alert('Per favore, seleziona un file .csv');
  }
}

function triggerFileInput() {
  fileInput.value.click();
}

function handleSubmit() {
  if (selectedFile.value) {
    emit('submit-import', selectedFile.value);
  }
}

function handleClose() {
  selectedFile.value = null;
  emit('close');
}
</script>

<template>
  <BaseModal :show="show" @close="handleClose">
    <template #header>
      <h3>Importa Operazioni da CSV</h3>
    </template>

    <div v-if="!importSummary" class="import-content">
      <div class="file-input-wrapper">
        <BaseButton variant="secondary" @click="triggerFileInput">
          <UploadIcon />
          <span>Scegli File</span>
        </BaseButton>
        <span class="file-name">{{ fileName }}</span>
        <input
          ref="fileInput"
          type="file"
          accept=".csv"
          @change="handleFileChange"
          hidden
        />
      </div>

      <div class="modal-actions">
        <BaseButton variant="secondary" @click="handleClose">Annulla</BaseButton>
        <BaseButton
          variant="primary"
          @click="handleSubmit"
          :disabled="!selectedFile || loading"
        >
          <span v-if="loading">Importazione...</span>
          <span v-else>Importa</span>
        </BaseButton>
      </div>
    </div>

    <div v-else class="summary-content">
      <h4>Riepilogo Importazione</h4>
      <div class="summary-grid">
        <div class="summary-item success">
          <span class="count">{{ importSummary.new_trades_imported }}</span>
          <span class="label">Nuovi Trade Importati</span>
        </div>
        <div class="summary-item skipped">
          <span class="count">{{ importSummary.duplicate_trades_skipped }}</span>
          <span class="label">Duplicati Saltati</span>
        </div>
        <div class="summary-item errors">
          <span class="count">{{ importSummary.errors_found }}</span>
          <span class="label">Errori Riscontrati</span>
        </div>
      </div>

      <div v-if="importSummary.errors && importSummary.errors.length > 0" class="error-details">
        <h5>Dettaglio Errori:</h5>
        <ul>
          <li v-for="(error, index) in importSummary.errors" :key="index">
            <span v-if="error.rows">Righe: {{ error.rows.join(', ') }}</span>
            <span v-if="error.trade_number"> | Trade #: {{ error.trade_number }}</span>
            <p><strong>Errore:</strong> {{ error.error }}</p>
          </li>
        </ul>
      </div>

       <div class="modal-actions">
        <BaseButton variant="primary" @click="handleClose">Chiudi</BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.import-content, .summary-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-lg);
  border: 2px dashed var(--semantic-color-border-neutral);
  border-radius: var(--semantic-border-radius-lg);
  background-color: var(--semantic-color-bg-subtle);
}

.file-name {
  font-family: var(--base-font-family-mono);
  color: var(--semantic-color-text-subtle);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  padding-top: var(--semantic-size-stack-md);
  border-top: 1px solid var(--semantic-color-border-neutral);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-lg);
  background-color: var(--semantic-color-bg-subtle);
  text-align: center;
}

.summary-item .count {
  font: var(--semantic-font-style-heading-xl);
}
.summary-item .label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-subtle);
}
.summary-item.success .count { color: var(--semantic-color-text-success); }
.summary-item.skipped .count { color: var(--semantic-color-text-warning); }
.summary-item.errors .count { color: var(--semantic-color-text-danger); }

.error-details {
  max-height: 200px;
  overflow-y: auto;
  padding: var(--semantic-size-inset-md);
  background-color: var(--semantic-color-bg-subtle);
  border-radius: var(--semantic-border-radius-md);
  font-size: 0.9em;
}

.error-details ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.error-details li {
  padding: var(--semantic-size-inset-sm);
  border-bottom: 1px solid var(--semantic-color-border-neutral);
}
.error-details li:last-child {
  border-bottom: none;
}
.error-details p {
  margin: 0;
  padding-top: 4px;
}
</style>
