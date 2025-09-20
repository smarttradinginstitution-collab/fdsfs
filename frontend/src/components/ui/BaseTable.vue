<!--
// =============================================================================
// FILE: components/ui/BaseTable.vue
// DESCRIZIONE: Componente UI di base per tabelle, ora con supporto per diverse
// dimensioni di testo tramite la prop `size`.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';

// --- PROPS ---
const props = defineProps({
  headers: {
    type: Array,
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['medium', 'small', 'x-small'].includes(value),
  },
  rowClickable: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['row-click']);

const tableClass = computed(() => {
  return ['table', `table--${props.size}`];
});
</script>

<template>
  <div class="table-container">
    <table :class="tableClass">
      <thead>
        <tr>
          <th v-for="header in headers" :key="header.key">{{ header.text }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in items"
          :key="item.id"
          :class="{ 'row-clickable': rowClickable }"
          @click="rowClickable && emit('row-click', item)"
        >
          <td v-for="header in headers" :key="header.key" :data-label="header.text">
            <slot :name="header.key" :item="item">
              {{ item[header.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-container {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--semantic-color-border-subtle);
  border-radius: 1.5rem;
  /* Per nascondere le linee verticali che escono dal contenitore */
  overflow: hidden;
}
.table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
  /* Spaziatura tra le celle per le linee verticali */
  border-spacing: 0;
}
th, td {
  border-bottom: 1px solid var(--semantic-color-border-subtle);
  padding: var(--semantic-size-inset-md);
  text-align: left;
}
th {
  background-color: var(--semantic-color-surface-page);
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}
td {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
}
/* Aggiunge la linea verticale */
th:not(:last-child),
td:not(:last-child) {
  border-right: 1px solid var(--semantic-color-border-subtle);
}
/* Stili per la dimensione piccola */
.table--small th, .table--small td {
  padding-top: var(--semantic-size-inset-sm);
  padding-bottom: var(--semantic-size-inset-sm);
}
.table--small th {
  font: var(--semantic-font-style-label-sm);
}
.table--small td {
  font: var(--semantic-font-style-body-xs);
}
/* Stili per la dimensione extra piccola */
.table--x-small th, .table--x-small td {
  padding-top: var(--semantic-size-inset-xs);
  padding-bottom: var(--semantic-size-inset-xs);
}
.table--x-small th {
  font: var(--semantic-font-style-label-xs);
}
.table--x-small td {
  font: var(--semantic-font-style-body-xxs);
}
tbody tr:hover {
  background-color: var(--semantic-color-surface-secondary);
}
.row-clickable {
  cursor: pointer;
}
/* === Stili per la Responsività === */
@media (max-width: 768px) {
  .table-container {
    border: none;
    border-radius: 0;
    overflow-x: visible;
  }
  .table {
    white-space: normal;
    border-spacing: 0;
  }
  .table thead {
    display: none;
  }
  .table tbody tr {
    display: block;
    margin-bottom: var(--semantic-size-stack-md);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-lg);
    padding: var(--semantic-size-inset-sm);
    background-color: var(--semantic-color-surface-primary);
  }
  .table td {
    display: block;
    text-align: right;
    padding-left: 50%;
    position: relative;
    border: none;
    border-bottom: 1px solid var(--semantic-color-border-subtle);
    padding-top: var(--semantic-size-inset-sm);
    padding-bottom: var(--semantic-size-inset-sm);
  }
  .table tr:last-child td:last-child {
    border-bottom: none;
  }
  .table td::before {
    content: attr(data-label);
    position: absolute;
    left: var(--semantic-size-inset-sm);
    width: 45%;
    padding-right: var(--semantic-size-inset-sm);
    white-space: nowrap;
    text-align: left;
    font-weight: var(--semantic-font-weight-bold);
    color: var(--semantic-color-text-secondary);
    font-size: var(--semantic-font-style-label-sm);
  }
  th:not(:last-child),
  td:not(:last-child) {
    border-right: none;
  }
}
</style>
