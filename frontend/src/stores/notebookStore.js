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
    // Getter to get the list of all folders
    allFolders: (state) => state.folders,

    // Getter to get the notes for the currently selected folder
    notesInSelectedFolder: (state) => state.notes,

    // Getter to find the full object of the selected folder
    selectedFolder: (state) => {
      return state.folders.find(f => f.id === state.selectedFolderId) || null;
    },

    // Getter to find the full object of the selected note
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
        // If no folder is selected, or the selected one no longer exists, select the first one.
        if (!this.selectedFolderId || !this.folders.some(f => f.id === this.selectedFolderId)) {
          if (this.folders.length > 0) {
            this.selectFolder(this.folders[0].id);
          } else {
            this.notes = []; // No folders, so no notes
          }
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
        // Add the new folder to the state and select it
        this.folders.push(response.data);
        this.selectFolder(response.data.id);
        // No need for a full refetch, optimistic update is fine
      } catch (err) {
        console.error('Error creating folder:', err);
        this.error = err.response?.data?.detail || 'Failed to create folder.';
        throw err; // Re-throw to be caught in the component
      } finally {
        this.isLoadingFolders = false;
      }
    },

    async deleteFolder(folderId) {
        this.isLoadingFolders = true;
        try {
            await apiClient.delete(`/notebook/folders/${folderId}`);
            // After deletion, refetch the folders to update the list
            // and handle re-selection logic correctly.
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
        this.isLoadingNotes = true;
        this.error = null;
        try {
            // A folder contains its notes, so we just need to find the folder
            const folder = this.folders.find(f => f.id === folderId);
            this.notes = folder ? folder.notes : [];
        } catch (err) {
            console.error(`Error fetching notes for folder ${folderId}:`, err);
            this.error = 'Failed to load notes for the selected folder.';
            this.notes = [];
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async createNote(noteData) {
        this.isLoadingNotes = true;
        try {
            await apiClient.post('/notebook/notes', noteData);
            // Refetch all folders to get the updated note list within the folder
            await this.fetchFolders();
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
            await apiClient.put(`/notebook/notes/${noteId}`, noteData);
            await this.fetchFolders(); // Refetch for consistency
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
            await this.fetchFolders(); // Refetch for consistency
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
        this.selectedNoteId = null; // Deselect note when folder changes
        this.fetchNotesForFolder(folderId);
      }
    },

    selectNote(noteId) {
      this.selectedNoteId = noteId;
    },

    // Action to deselect a note, useful for showing the note list again
    deselectNote() {
        this.selectedNoteId = null;
    }
  },
});