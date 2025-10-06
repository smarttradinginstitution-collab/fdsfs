<template>
  <teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">New Trade Note</h2>
          <button class="close-button" @click="$emit('close')">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="note-title">Note Title</label>
            <input
              id="note-title"
              v-model="title"
              type="text"
              class="form-input"
              placeholder="Enter note title..."
            />
          </div>
          <div class="form-group">
             <div v-if="selectedTrade" class="selected-trade-info">
              <p>
                ✓ Linked to: {{ selectedTrade.asset.symbol }} on {{ new Date(selectedTrade.entry_timestamp).toLocaleDateString() }}
              </p>
              <button @click="selectedTrade = null" class="unlink-button">Unlink</button>
            </div>
            <button v-else class="link-trade-button" @click="fetchRecentTrades">
              {{ showTrades ? 'Hide Trades' : 'Link Trade' }}
            </button>
          </div>
          <div v-if="showTrades" class="trades-list-container">
            <div v-if="isLoadingTrades" class="loading-spinner">Loading...</div>
            <table v-else-if="recentTrades.length > 0" class="trades-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Symbol</th>
                  <th>P&L</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trade in recentTrades" :key="trade.id">
                  <td>{{ new Date(trade.entry_timestamp).toLocaleDateString() }}</td>
                  <td>{{ trade.asset.symbol }}</td>
                  <td :class="trade.p_l >= 0 ? 'text-green' : 'text-red'">{{ trade.p_l }}</td>
                  <td>
                    <button @click="selectTrade(trade)" class="select-button">Select</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-state">No recent trades found.</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="button-secondary" @click="$emit('close')">Cancel</button>
          <button class="button-primary" @click="handleSave">Create Note</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '../../services/api';

defineProps({
  isOpen: Boolean,
});
const emit = defineEmits(['close', 'create']);

const title = ref('');
const recentTrades = ref([]);
const selectedTrade = ref(null);
const showTrades = ref(false);
const isLoadingTrades = ref(false);

async function fetchRecentTrades() {
  if (showTrades.value) {
    showTrades.value = false;
    return;
  }

  isLoadingTrades.value = true;
  showTrades.value = true;
  try {
    const response = await apiClient.get('/trades/recent');
    recentTrades.value = response.data;
  } catch (error) {
    console.error("Failed to fetch recent trades:", error);
  } finally {
    isLoadingTrades.value = false;
  }
}

function selectTrade(trade) {
  selectedTrade.value = trade;
  showTrades.value = false;
}

function handleSave() {
  if (!title.value.trim()) {
    alert('Please enter a title for the note.');
    return;
  }
  emit('create', {
    title: title.value.trim(),
    trade_id: selectedTrade.value ? selectedTrade.value.id : null,
  });
  title.value = '';
  selectedTrade.value = null;
  recentTrades.value = [];
  showTrades.value = false;
}
</script>

<style lang="scss" scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.modal-title {
  font: var(--semantic-font-style-heading-lg);
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}

.modal-body {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-sm);
}

label {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}

.form-input {
  font: var(--semantic-font-style-body-base);
  padding: var(--semantic-size-inset-md);
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  color: var(--semantic-color-text-primary);
  width: 100%;
  &:focus {
    outline: none;
    border-color: var(--semantic-color-border-focus);
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-inset-md);
  padding: var(--semantic-size-inset-lg);
  border-top: 1px solid var(--semantic-color-border-default);
}

.button-primary, .button-secondary, .link-trade-button {
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-interactive);
  border: 1px solid transparent;
  cursor: pointer;
  font: var(--semantic-font-style-label-md);
}

.button-primary {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-primary);
}

.button-secondary {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
  border-color: var(--semantic-color-border-default);
}

.link-trade-button {
  background-color: var(--semantic-color-surface-secondary);
  border-color: var(--semantic-color-border-default);
  width: fit-content;
}

.trades-list-container {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
  th, td {
    padding: var(--semantic-size-inset-md);
    text-align: left;
    border-bottom: 1px solid var(--semantic-color-border-default);
  }
  th {
    font: var(--semantic-font-style-label-sm);
    background-color: var(--semantic-color-surface-secondary);
  }
  tbody tr:hover {
    background-color: var(--semantic-color-surface-secondary);
  }
}

.text-green { color: var(--semantic-color-text-success); }
.text-red { color: var(--semantic-color-text-danger); }
</style>