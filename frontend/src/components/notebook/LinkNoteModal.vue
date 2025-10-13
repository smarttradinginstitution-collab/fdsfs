<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <h3>Link Existing Note</h3>
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Search notes by title..."
        class="search-input"
      />
      <div v-if="isLoading" class="loading-spinner">
        <p>Loading unlinked notes...</p>
      </div>
      <ul v-else-if="filteredNotes.length" class="notes-list">
        <li
          v-for="note in filteredNotes"
          :key="note.id"
          @click="selectNote(note.id)"
          class="note-item"
        >
          {{ note.title }}
        </li>
      </ul>
      <div v-else>
        <p>No unlinked notes found.</p>
      </div>
      <button @click="close" class="btn-secondary">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineProps, defineEmits, watch } from 'vue';
import { useNotebookStore } from '@/stores/notebookStore';

const props = defineProps({
  isOpen: Boolean,
});

const emit = defineEmits(['close', 'link-note']);

const notebookStore = useNotebookStore();
const searchTerm = ref('');

const filteredNotes = computed(() => {
  if (!searchTerm.value) {
    return notebookStore.unlinkedNotes;
  }
  return notebookStore.unlinkedNotes.filter(note =>
    note.title.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

const selectNote = (noteId) => {
  emit('link-note', noteId);
};

const close = () => {
  emit('close');
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    notebookStore.fetchUnlinkedNotes();
  }
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.search-input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
}
.notes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}
.note-item {
  padding: 0.75rem;
  cursor: pointer;
}
.note-item:hover {
  background-color: #f0f0f0;
}
</style>