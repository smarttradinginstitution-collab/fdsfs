// frontend/src/stores/notebookStore.js
import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useNotebookStore = defineStore('notebook', {
  state: () => ({
    folders: [],
    notes: [],
    selectedFolderId: null,
    selectedNoteId: null,
    isLoadingFolders: false,
    isLoadingNotes: false,
    error: null,
  }),

  getters: {
    allFolders: (state) => state.folders,
    notesInSelectedFolder: (state) => state.notes,
    selectedFolder: (state) => {
      return state.folders.find(f => f.id === state.selectedFolderId) || null;
    },
    selectedNote: (state) => {
      return state.notes.find(n => n.id === state.selectedNoteId) || null;
    },
  },

  actions: {
    // --- FOLDER ACTIONS ---

    async fetchFolders() {
      this.isLoadingFolders = true;
      this.error = null;
      try {
        const response = await apiClient.get('/notebook/folders');
        this.folders = response.data;

        if (!this.selectedFolderId && this.folders.length > 0) {
          this.selectFolder(this.folders[0].id);
        } else if (this.selectedFolderId) {
          // If a folder is selected, ensure its notes are loaded
          this.fetchNotesForFolder(this.selectedFolderId);
        } else {
          this.notes = [];
        }
      } catch (err) {
        console.error('Error fetching notebook folders:', err);
        this.error = err.response?.data?.detail || 'Failed to fetch folders.';
        this.folders = [];
      } finally {
        this.isLoadingFolders = false;
      }
    },

    async createFolder(folderData) {
      this.isLoadingFolders = true;
      try {
        const response = await apiClient.post('/notebook/folders', folderData);
        this.folders.push(response.data);
        this.selectFolder(response.data.id);
      } catch (err) {
        console.error('Error creating folder:', err);
        this.error = err.response?.data?.detail || 'Failed to create folder.';
        throw err;
      } finally {
        this.isLoadingFolders = false;
      }
    },

    async deleteFolder(folderId) {
        this.isLoadingFolders = true;
        try {
            await apiClient.delete(`/notebook/folders/${folderId}`);
            await this.fetchFolders();
        } catch (err) {
            console.error('Error deleting folder:', err);
            this.error = err.response?.data?.detail || 'Failed to delete folder.';
            throw err;
        } finally {
            this.isLoadingFolders = false;
        }
    },

    // --- NOTE ACTIONS ---

    async fetchNotesForFolder(folderId) {
        const folder = this.folders.find(f => f.id === folderId);
        this.notes = folder ? folder.notes.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at)) : [];
    },

    async createNote(noteData) {
        this.isLoadingNotes = true;
        try {
            const response = await apiClient.post('/notebook/notes', noteData);
            const newNote = response.data;
            // Add the new note to the local state for immediate UI update
            this.notes.unshift(newNote);
            // Also add it to the folder's internal notes list
            const parentFolder = this.folders.find(f => f.id === newNote.folder_id);
            if (parentFolder) {
                parentFolder.notes.unshift(newNote);
            }
        } catch (err) {
            console.error('Error creating note:', err);
            this.error = err.response?.data?.detail || 'Failed to create note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async updateNote(noteId, noteData) {
        this.isLoadingNotes = true;
        try {
            const response = await apiClient.put(`/notebook/notes/${noteId}`, noteData);
            const updatedNote = response.data;
            // Update the note in the local lists
            const noteIndex = this.notes.findIndex(n => n.id === noteId);
            if (noteIndex !== -1) {
                this.notes[noteIndex] = updatedNote;
            }
            const parentFolder = this.folders.find(f => f.id === updatedNote.folder_id);
            if (parentFolder) {
                const folderNoteIndex = parentFolder.notes.findIndex(n => n.id === noteId);
                if (folderNoteIndex !== -1) {
                    parentFolder.notes[folderNoteIndex] = updatedNote;
                }
            }
        } catch (err) {
            console.error('Error updating note:', err);
            this.error = err.response?.data?.detail || 'Failed to update note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async deleteNote(noteId) {
        this.isLoadingNotes = true;
        try {
            await apiClient.delete(`/notebook/notes/${noteId}`);
            // Remove from local state for immediate UI update
            this.notes = this.notes.filter(n => n.id !== noteId);
            const parentFolder = this.folders.find(f => f.id === this.selectedFolderId);
            if (parentFolder) {
                parentFolder.notes = parentFolder.notes.filter(n => n.id !== noteId);
            }
        } catch (err) {
            console.error('Error deleting note:', err);
            this.error = err.response?.data?.detail || 'Failed to delete note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    // --- SELECTION ACTIONS ---

    selectFolder(folderId) {
      if (this.selectedFolderId !== folderId) {
        this.selectedFolderId = folderId;
        this.selectedNoteId = null;
        this.fetchNotesForFolder(folderId);
      }
    },

    selectNote(noteId) {
      this.selectedNoteId = noteId;
    },

    deselectNote() {
        this.selectedNoteId = null;
    }
  },
});