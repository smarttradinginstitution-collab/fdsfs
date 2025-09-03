<!--
// =============================================================================
// FILE: components/ui/BaseTable.vue
// DESCRIZIONE: Questo è un componente UI di base per visualizzare dati in
// una tabella. È progettato per essere flessibile e riutilizzabile in tutta
// l'applicazione.
// =============================================================================
-->

<script setup>
// --- PROPS ---
defineProps({
  // `headers` è un array di oggetti che definisce le colonne della tabella.
  // Ogni oggetto deve avere:
  // - `key`: Un identificatore univoco (corrisponde alla chiave nell'oggetto `item`).
  // - `text`: Il testo da mostrare nell'intestazione della colonna.
  // Esempio: [{ key: 'ticker', text: 'Ticker' }]
  headers: {
    type: Array,
    required: true,
  },
  // `items` è un array di oggetti che contiene i dati delle righe.
  // Ogni oggetto rappresenta una riga.
  // Esempio: [{ id: 1, ticker: 'AAPL', pnl: 150.25 }]
  items: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <!-- Il contenitore serve per gestire lo scrolling orizzontale su schermi piccoli. -->
  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <!-- Creiamo un'intestazione `<th>` per ogni oggetto nell'array `headers`. -->
          <th v-for="header in headers" :key="header.key">{{ header.text }}</th>
        </tr>
      </thead>
      <tbody>
        <!-- Creiamo una riga `<tr>` per ogni oggetto nell'array `items`. -->
        <tr v-for="item in items" :key="item.id">
          <!-- Creiamo una cella `<td>` per ogni colonna definita in `headers`. -->
          <!-- Aggiungiamo l'attributo `data-label` che useremo nel CSS per la vista mobile. -->
          <td v-for="header in headers" :key="header.key" :data-label="header.text">
            <!--
            Questa è la parte più potente: usiamo uno "slot nominato dinamico".
            - `<slot :name="header.key" ...>`: Crea uno slot con il nome della chiave
              della colonna (es. 'pnl', 'ticker').
            - Questo permette al componente genitore di "sovrascrivere" come viene
              visualizzata una specifica cella, fornendo un template personalizzato.
              Esempio in DashboardView: `<template #pnl="{ item }">...</template>`
            - Se il genitore non fornisce un template per quello slot, viene mostrato
              il contenuto di default qui sotto.
            -->
            <slot :name="header.key" :item="item">
              <!-- Contenuto di default: mostra semplicemente il valore della cella.
                   Esempio: `item['ticker']` mostrerà 'AAPL'. -->
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
  /* Rimuoviamo l'overflow, la tabella andrà a capo da sola su mobile. */
}
.table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}
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
tbody tr:hover {
  background-color: var(--semantic-color-surface-secondary);
}

/* === Stili per la Responsività (Card List Transformation) === */
@media (max-width: 768px) {
  .table {
    white-space: normal; /* Permettiamo al testo di andare a capo */
  }

  /* Nascondiamo le intestazioni della tabella */
  .table thead {
    display: none;
  }

  /* Trasformiamo le righe in card */
  .table tr {
    display: block;
    margin-bottom: var(--semantic-size-stack-md);
    border: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-surface);
    padding: var(--semantic-size-inset-sm);
  }

  /* Trasformiamo le celle in blocchi */
  .table td {
    display: block;
    text-align: right; /* Allineiamo il valore a destra */
    padding-left: 50%; /* Creiamo spazio a sinistra per l'etichetta */
    position: relative;
    border-top: none; /* Rimuoviamo i bordi interni */
    padding-top: var(--base-size-spacing-1);
    padding-bottom: var(--base-size-spacing-1);
  }

  /* Aggiungiamo l'etichetta usando lo pseudo-elemento ::before */
  .table td::before {
    content: attr(data-label); /* Prendiamo il testo dall'attributo data-label */
    position: absolute;
    left: var(--base-size-spacing-2);
    width: 45%;
    padding-right: var(--base-size-spacing-2);
    white-space: nowrap;
    text-align: left;
    font-weight: var(--base-font-weight-bold);
    color: var(--semantic-color-text-secondary);
  }

  /* Aggiungiamo un bordo solo alla prima cella della "card" */
  .table td:first-child {
    border-top: none;
  }
  .table tr:first-child td:first-child {
      border-top: none;
  }
}
</style>
