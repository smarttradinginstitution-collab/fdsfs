<script setup>
import { onMounted } from 'vue';
import { useRequestLogStore } from '@/stores/requestLogStore';
import { storeToRefs } from 'pinia';
import BaseButton from '@/components/ui/BaseButton.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import ArrowUpIcon from '@/components/icons/ArrowUpIcon.vue';
import ArrowDownIcon from '@/components/icons/ArrowDownIcon.vue';

// Store
const requestLogStore = useRequestLogStore();
const { logs, isLoading, pagination, sorting, filters } = storeToRefs(requestLogStore);

// Actions
const { fetchRequestLogs, changePage, changeSort, applyFilter, clearAllLogs } = requestLogStore;

// Data Fetching
onMounted(() => {
  fetchRequestLogs();
});

// Helper to format date
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('it-IT', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const handleFilterInput = (event) => {
  const value = event.target.value;
  applyFilter(value ? Number(value) : null);
};

</script>

<template>
  <div class="request-logs-view">
    <header class="view-header">
      <h1>Monitoraggio Richieste API</h1>
      <p>Questa pagina mostra i tempi di risposta e altri dettagli per le richieste al backend.</p>
    </header>

    <!-- Controls -->
    <div class="controls-bar">
      <div class="filter-group">
        <label for="status-filter">Filtra per Status:</label>
        <input
          id="status-filter"
          type="number"
          class="filter-input"
          placeholder="Es. 200, 404..."
          :value="filters.statusCode"
          @input="handleFilterInput"
        />
      </div>
      <BaseButton variant="danger" @click="clearAllLogs">
        <TrashIcon />
        <span>Svuota Log</span>
      </BaseButton>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>Caricamento dei log in corso...</p>
    </div>

    <!-- Table -->
    <div v-else class="logs-container">
      <div class="table-wrapper">
        <table class="logs-table">
          <thead>
            <tr>
              <th @click="changeSort('created_at')">
                Timestamp
                <span v-if="sorting.by === 'created_at'">
                  <ArrowUpIcon v-if="sorting.order === 'asc'" class="sort-icon" />
                  <ArrowDownIcon v-else class="sort-icon" />
                </span>
              </th>
              <th @click="changeSort('method')">
                Metodo
                 <span v-if="sorting.by === 'method'">
                  <ArrowUpIcon v-if="sorting.order === 'asc'" class="sort-icon" />
                  <ArrowDownIcon v-else class="sort-icon" />
                </span>
              </th>
              <th @click="changeSort('path')">
                Path
                 <span v-if="sorting.by === 'path'">
                  <ArrowUpIcon v-if="sorting.order === 'asc'" class="sort-icon" />
                  <ArrowDownIcon v-else class="sort-icon" />
                </span>
              </th>
              <th @click="changeSort('status_code')">
                Status
                 <span v-if="sorting.by === 'status_code'">
                  <ArrowUpIcon v-if="sorting.order === 'asc'" class="sort-icon" />
                  <ArrowDownIcon v-else class="sort-icon" />
                </span>
              </th>
              <th @click="changeSort('response_time_ms')">
                Tempo Risposta (ms)
                 <span v-if="sorting.by === 'response_time_ms'">
                  <ArrowUpIcon v-if="sorting.order === 'asc'" class="sort-icon" />
                  <ArrowDownIcon v-else class="sort-icon" />
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="logs.length === 0">
              <td colspan="5" class="no-data-cell">Nessun log trovato che corrisponda ai filtri applicati.</td>
            </tr>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ formatDate(log.created_at) }}</td>
              <td>{{ log.method }}</td>
              <td class="path-cell">{{ log.path }}</td>
              <td>
                <span :class="`status-badge status-${String(log.status_code)[0]}`">{{ log.status_code }}</span>
              </td>
              <td class="time-cell">{{ log.response_time_ms }} ms</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-controls">
      <span class="total-results">Totale: {{ pagination.total }} risultati</span>
      <div class="buttons">
        <BaseButton variant="secondary" :disabled="pagination.offset === 0" @click="changePage(pagination.offset - pagination.limit)">Precedente</BaseButton>
        <BaseButton variant="secondary" :disabled="pagination.offset + pagination.limit >= pagination.total" @click="changePage(pagination.offset + pagination.limit)">Successivo</BaseButton>
      </div>
    </div>

  </div>
</template>

<style lang="scss" scoped>
.request-logs-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.view-header {
  margin-bottom: var(--semantic-size-stack-sm);
  h1 {
    font: var(--semantic-font-style-heading-xl);
    color: var(--semantic-color-text-primary);
  }
  p {
    font: var(--semantic-font-style-body-lg);
    color: var(--semantic-color-text-secondary);
    margin-top: var(--semantic-size-stack-xs);
  }
}

.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: var(--semantic-size-stack-sm);
  align-items: center;
  label {
    font: var(--semantic-font-style-body-lg);
  }
  .filter-input {
    padding: var(--semantic-size-inset-sm);
    border-radius: var(--semantic-border-radius-md);
    border: 1px solid var(--semantic-color-border-default);
    min-width: 150px;
  }
}

.loading-state {
  text-align: center;
  padding: var(--semantic-size-inset-2xl);
  font: var(--semantic-font-style-body-lg);
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-lg);
}

.logs-table {
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: var(--semantic-size-inset-md);
    text-align: left;
    border-bottom: 1px solid var(--semantic-color-border-default);
  }

  th {
    font: var(--semantic-font-style-heading-xs);
    background-color: var(--semantic-color-background-default-subtle);
    cursor: pointer;
    user-select: none;
    &:hover {
      background-color: var(--semantic-color-background-default-hover);
    }
    .sort-icon {
        display: inline-block;
        vertical-align: middle;
        width: 1em;
        height: 1em;
        margin-left: 4px;
    }
  }

  tr:last-child td {
    border-bottom: none;
  }

  .no-data-cell {
    text-align: center;
    padding: var(--semantic-size-inset-2xl);
    color: var(--semantic-color-text-secondary);
  }

  .path-cell {
    word-break: break-all;
  }

  .time-cell {
      text-align: right;
  }

  .status-badge {
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: bold;
    color: white;
    &.status-2 { background-color: var(--semantic-color-background-success-default); }
    &.status-3 { background-color: var(--semantic-color-background-info-default); }
    &.status-4 { background-color: var(--semantic-color-background-warning-default); }
    &.status-5 { background-color: var(--semantic-color-background-danger-default); }
  }
}

.pagination-controls {
    margin-top: var(--semantic-size-stack-md);
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
}
</style>