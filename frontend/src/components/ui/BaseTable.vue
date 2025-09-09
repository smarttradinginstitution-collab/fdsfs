<!--
// =============================================================================
// FILE: components/ui/BaseTable.vue
// DESCRIZIONE: Componente UI di base per tabelle, ora con supporto per diverse
// dimensioni di testo tramite la prop `size`.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';

/**
 * Formats a cell value for display. If the value is an ISO date string,
 * it's converted to a localized, user-friendly format. Otherwise, it's
 * returned as is.
 * @param {*} value The cell value.
 * @returns {string} The formatted value.
 */
function formatCell(value) {
  // Regex to check for a string that looks like an ISO 8601 timestamp (ending in Z)
  const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;

  if (typeof value === 'string' && isoDateRegex.test(value)) {
    const date = new Date(value);
    // Check if the created date is valid
    if (isNaN(date)) {
      return value; // Return original string if date is invalid
    }
    // Format the date and time according to the user's local timezone and conventions.
    // Using 'it-IT' as a specific locale for consistency.
    const options = {
      year: '2-digit',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false, // Use 24-hour format
    };
    return date.toLocaleString('it-IT', options);
  }

  // For any other type of value, return it without modification.
  return value;
}


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
  // Nuova prop per controllare la dimensione del font
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['medium', 'small', 'x-small'].includes(value),
  }
});

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
        <tr v-for="item in items" :key="item.id">
          <td v-for="header in headers" :key="header.key" :data-label="header.text">
            <slot :name="header.key" :item="item">
              {{ formatCell(item[header.key]) }}
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
}
.table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

/* Stili di default (medium) */
th {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  text-align: left;
  padding: var(--semantic-size-inset-md);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
}
td {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
  padding: var(--semantic-size-inset-md);
  border-top: var(--base-border-width-1) solid var(--semantic-color-border-subtle);
}

/* Stili per la dimensione piccola */
.table--small th {
    font: var(--semantic-font-style-label-sm);
    padding-top: var(--semantic-size-inset-sm);
    padding-bottom: var(--semantic-size-inset-sm);
}

/* Stili per la dimensione extra piccola */
.table--x-small th {
    font: var(--semantic-font-style-label-xs);
    padding-top: var(--semantic-size-inset-xs);
    padding-bottom: var(--semantic-size-inset-xs);
}
.table--x-small td {
    font: var(--semantic-font-style-body-xxs);
    padding-top: var(--semantic-size-inset-xs);
    padding-bottom: var(--semantic-size-inset-xs);
}
.table--small td {
    font: var(--semantic-font-style-body-xs);
    padding-top: var(--semantic-size-inset-sm);
    padding-bottom: var(--semantic-size-inset-sm);
}


tbody tr:hover {
  background-color: var(--semantic-color-surface-secondary);
}

/* === Stili per la Responsività === */
@media (max-width: 768px) {
  .table { white-space: normal; }
  .table thead { display: none; }
  .table tr {
    display: block;
    margin-bottom: var(--semantic-size-stack-md);
    border: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    padding: var(--semantic-size-inset-sm);
  }
  .table td {
    display: block;
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-top: none;
    padding-top: var(--base-size-spacing-1);
    padding-bottom: var(--base-size-spacing-1);
  }
  .table td::before {
    content: attr(data-label);
    position: absolute;
    left: var(--base-size-spacing-2);
    width: 45%;
    padding-right: var(--base-size-spacing-2);
    white-space: nowrap;
    text-align: left;
    font-weight: var(--base-font-weight-bold);
    color: var(--semantic-color-text-secondary);
  }
  .table td:first-child { border-top: none; }
  .table tr:first-child td:first-child { border-top: none; }
}
</style>
