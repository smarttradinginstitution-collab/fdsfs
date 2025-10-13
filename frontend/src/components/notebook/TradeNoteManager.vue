<template>
  <div class="trade-note-manager">
    <div v-if="isLoading" class="loading-spinner">
      <p>Loading note...</p>
    </div>
    <div v-else-if="!linkedNote" class="no-note-actions">
      <button @click="handleCreateNote" class="btn-primary">
        + Create Note for this Trade
      </button>
      <button @click="openLinkModal" class="btn-secondary">
        🔗 Link Existing Note
      </button>
    </div>
    <div v-else class="note-display">
      <div v-if="!isEditing">
        <div class="note-header">
          <h3>{{ linkedNote.title }}</h3>
          <div class="note-actions">
            <button @click="isEditing = true" class="btn-icon">✏️</button>
            <button @click="goToNote" class="btn-icon">↗️</button>
            <button @click="confirmUnlink" class="btn-icon">🚫</button>
          </div>
        </div>
        <div class="note-content" v-html="linkedNote.content"></div>
      </div>
      <div v-else>
        <NoteEditor :note-id="linkedNote.id" @close-editor="isEditing = false" />
      </div>
    </div>

    <!-- Modals -->
    <LinkNoteModal
      :is-open="isLinkModalOpen"
      @close="isLinkModalOpen = false"
      @link-note="handleLinkNote"
    />
    <ConfirmModal
      :is-open="isUnlinkConfirmModalOpen"
      title="Unlink Note"
      message="Are you sure you want to unlink this note from the trade?"
      @confirm="handleUnlinkNote"
      @close="isUnlinkConfirmModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useNotebookStore } from '@/stores/notebookStore';
import NoteEditor from './NoteEditor.vue';
import LinkNoteModal from './LinkNoteModal.vue';
import ConfirmModal from '../ui/ConfirmModal.vue';

const props = defineProps({
  tradeId: {
    type: String,
    required: true,
  },
});

const router = useRouter();
const notebookStore = useNotebookStore();

const linkedNote = ref(null);
const isLoading = ref(true);
const isEditing = ref(false);
const isLinkModalOpen = ref(false);
const isUnlinkConfirmModalOpen = ref(false);

const fetchNote = async () => {
  isLoading.value = true;
  try {
    linkedNote.value = await notebookStore.fetchNoteForTrade(props.tradeId);
  } catch (error) {
    console.error('Failed to fetch note for trade:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleCreateNote = async () => {
  try {
    const newNote = await notebookStore.createNoteForTrade({
      title: `Note for Trade ${props.tradeId}`, // A default title
      tradeId: props.tradeId,
    });
    linkedNote.value = newNote;
    isEditing.value = true; // Open editor for the new note
  } catch (error) {
    console.error('Failed to create note for trade:', error);
    // Handle error in UI
  }
};

const openLinkModal = () => {
  isLinkModalOpen.value = true;
};

const handleLinkNote = async (noteId) => {
  try {
    const updatedNote = await notebookStore.linkNoteToTrade(noteId, props.tradeId);
    linkedNote.value = updatedNote;
    isLinkModalOpen.value = false;
  } catch (error) {
    console.error('Failed to link note:', error);
    // Handle error in UI
  }
};

const confirmUnlink = () => {
  isUnlinkConfirmModalOpen.value = true;
};

const handleUnlinkNote = async () => {
  if (!linkedNote.value) return;
  try {
    await notebookStore.unlinkNoteFromTrade(linkedNote.value.id);
    linkedNote.value = null;
  } catch (error) {
    console.error('Failed to unlink note:', error);
    // Handle error in UI
  }
};

const goToNote = () => {
  if (linkedNote.value) {
    router.push({ name: 'notebook', query: { note_id: linkedNote.value.id, folder_id: linkedNote.value.folder_id } });
  }
};

onMounted(fetchNote);

watch(() => props.tradeId, fetchNote);
</script>

<style scoped>
.trade-note-manager {
  padding: 1rem;
}
.no-note-actions {
  display: flex;
  gap: 1rem;
}
.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.note-actions {
  display: flex;
  gap: 0.5rem;
}
.note-content {
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 4px;
}
</style>