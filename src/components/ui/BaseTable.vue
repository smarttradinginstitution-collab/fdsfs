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
    margin-bottom: clamp(var(--semantic-size-stack-sm), 4vw, var(--semantic-size-stack-md));
    border: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    padding: clamp(var(--semantic-size-inset-sm), 3vw, var(--semantic-size-inset-md));
  }
  .table td {
    display: flex; /* Usiamo flex per un miglior allineamento */
    justify-content: space-between; /* Allinea label e valore */
    align-items: center;
    text-align: right;
    padding: clamp(var(--base-size-spacing-2), 2vw, var(--base-size-spacing-3)) 0;
    position: relative;
    border-top: var(--base-border-width-1) solid var(--semantic-color-border-subtle);
  }
  .table td::before {
    content: attr(data-label);
    font-weight: var(--base-font-weight-medium);
    color: var(--semantic-color-text-secondary);
    text-align: left;
    margin-right: var(--semantic-size-stack-sm); /* Spazio tra label e valore */
  }
  .table tr:first-of-type td:first-of-type {
    border-top: none;
  }
  .table td:first-of-type {
    padding-top: 0;
  }
  .table td:last-of-type {
    padding-bottom: 0;
  }
}
</style>
