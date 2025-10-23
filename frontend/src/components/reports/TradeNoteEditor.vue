<template>
  <div class="trade-note-editor-widget">
    <BaseWidget>
      <template #header>
        <span>Trade Note</span>
      </template>
      <div v-if="isLoading" class="loading-state">
        <p>Loading Note...</p>
      </div>
      <div v-else-if="store.selectedNote && store.selectedNote.trade_id === tradeId">
        <NoteEditor
          :key="store.selectedNote.id"
          :show-financial-data="false"
          :show-trade-details-link="false"
        />
      </div>
      <div v-else class="empty-state">
        <p>No note found for this trade.</p>
        <BaseButton @click="createNoteForTrade" :is-loading="isCreating">
          Create Note for this Trade
        </BaseButton>
      </div>
    </BaseWidget>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import BaseButton from '../ui/BaseButton.vue';
import NoteEditor from '../notebook/NoteEditor.vue';

const props = defineProps({
  tradeId: {
    type: String,
    required: true,
  },
  tradeDetails: {
    type: Object,
    required: true,
  }
});

const store = useNotebookStore();
const isLoading = ref(true);
const isCreating = ref(false);

const fetchNote = async () => {
  if (!props.tradeId) return;

  // Se la nota corretta è già selezionata, non fare nulla.
  if (store.selectedNote && store.selectedNote.trade_id === props.tradeId) {
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  try {
    const fetchedNote = await store.fetchNoteByTradeId(props.tradeId);
    if (fetchedNote) {
      store.selectNote(fetchedNote.id);
    } else {
      // Se non viene trovata nessuna nota, assicurati di deselezionare qualsiasi nota precedente
      store.deselectNote();
    }
  } catch (error) {
    if (error.response && error.response.status === 404) {
      if (store.selectedNote?.trade_id === props.tradeId) {
        store.deselectNote();
      }
    } else {
      console.error("Error fetching trade note:", error);
    }
  } finally {
    isLoading.value = false;
  }
};

const createNoteForTrade = async () => {
  isCreating.value = true;
  try {
    const tradeDate = new Date(props.tradeDetails.entry_timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    const symbol = props.tradeDetails.asset?.symbol ?? 'N/A';
    const title = `${symbol} : ${tradeDate}`;

    let tradeNotesFolder = store.folders.find(f => f.system_folder_identifier === 'TRADE_NOTES');
    if (!tradeNotesFolder) {
      await store.fetchFolders();
      tradeNotesFolder = store.folders.find(f => f.system_folder_identifier === 'TRADE_NOTES');
      if (!tradeNotesFolder) {
        throw new Error("Critical: Trade Notes system folder not found.");
      }
    }

    await store.createTradeNote({
      folderId: tradeNotesFolder.id,
      title,
      tradeId: props.tradeId,
    });

  } catch (error) {
    console.error("Error creating note for trade:", error);
  } finally {
    isCreating.value = false;
  }
};

onMounted(async () => {
  if (store.folders.length === 0) {
    await store.fetchFolders();
  }
  fetchNote();
});

watch(() => props.tradeId, () => {
  fetchNote();
});

</script>

<style lang="scss" scoped>
.loading-state, .empty-state {
  padding: var(--semantic-size-inset-xl);
  text-align: center;
  color: var(--semantic-color-text-secondary);

  p {
    margin-bottom: var(--semantic-size-inset-md);
  }
}
</style>