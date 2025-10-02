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
  // v-model per le righe selezionate
  selected: {
    type: Array,
    default: () => [],
  },
});

// --- EMITS ---
const emit = defineEmits(['update:selected']);

// --- LOGICA DEL COMPONENTE ---
const tableClass = computed(() => {
  return ['table', `table--${props.size}`];
});

// Controlla se tutte le righe sono selezionate per lo stato del checkbox principale
const allSelected = computed({
  get() {
    return props.items.length > 0 && props.selected.length === props.items.length;
  },
  set(value) {
    const selectedIds = value ? props.items.map(item => item.id) : [];
    emit('update:selected', selectedIds);
  }
});

const getCellAlignment = (header) => {
  if (header.align) {
    return `text-align: ${header.align};`;
  }
  return '';
};
</script>

<template>
  <div class="table-container">
    <table :class="tableClass">
      <thead>
        <tr>
          <th v-for="header in headers" :key="header.key" :style="getCellAlignment(header)">
            <!-- Se la colonna è 'checkbox', mostra il checkbox "seleziona tutto" -->
            <template v-if="header.key === 'checkbox'">
              <input type="checkbox" v-model="allSelected" />
            </template>
            <template v-else>
              {{ header.text }}
            </template>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" :class="{ 'selected-row': selected.includes(item.id) }">
          <td v-for="header in headers" :key="header.key" :data-label="header.text" :style="getCellAlignment(header)">
            <slot :name="header.key" :item="item">
              <!-- Logica per la cella checkbox -->
              <template v-if="header.key === 'checkbox'">
                <input type="checkbox" :value="item.id" :checked="selected.includes(item.id)" @change="$emit('update:selected', selected.includes(item.id) ? selected.filter(id => id !== item.id) : [...selected, item.id])"/>
              </template>
              <template v-else>
                {{ item[header.key] }}
              </template>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
.table-container {
  width: 100%;
  overflow-x: auto; /* Aggiunge lo scroll orizzontale se la tabella è troppo larga */
}
.table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

/* Stili di default (medium) */
th {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  text-transform: uppercase; // Testo maiuscolo come da requisito
  text-align: left;
  padding: var(--semantic-size-inset-md);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
  vertical-align: middle; // Allineamento verticale
}

td {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-md); // Padding verticale e orizzontale
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default); // Stesso bordo dell'header
  vertical-align: middle; // Allineamento verticale
}

/* Rimuoviamo il bordo superiore di default per evitare doppie linee */
td {
  border-top: none;
}

tbody tr:hover {
  background-color: var(--semantic-color-surface-secondary);
}

/* Stile per le righe selezionate */
.selected-row {
  background-color: var(--semantic-color-surface-secondary-selected); // Un token ipotetico, da creare se non esiste
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
@include media-down('md') {
  .table {
    white-space: normal;
  }
  .table thead {
    display: none;
  }
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
  .table td:first-child {
    border-top: none;
  }
  .table tr:first-child td:first-child {
    border-top: none;
  }
}
</style>
