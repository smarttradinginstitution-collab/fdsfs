<template>
  <div class="daily-journal-view">
    <div v-if="journalStore.isLoading">Loading...</div>
    <div v-else-if="!journalStore.journalDay">
      No journal entry for this day.
    </div>
    <div v-else class="main-content">
      <div class="left-column">
        <NoteEditor
          :note="journalStore.journalDay.note"
          :financialData="journalStore.journalDay"
          @update="updateNote"
        />
      </div>
      <div class="right-column">
        <Checklist :rules="journalStore.journalDay.rules" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useJournalStore } from '../stores/journalStore';
import NoteEditor from '../components/notebook/NoteEditor.vue';
import Checklist from '../components/journal/Checklist.vue';

const route = useRoute();
const journalStore = useJournalStore();

const updateNote = (noteData) => {
  journalStore.updateNote(noteData.id, {
    title: noteData.title,
    content: noteData.content,
  });
};

onMounted(() => {
  const date = route.params.date;
  if (date) {
    journalStore.getDay(date);
  }
});
</script>

<style scoped>
.daily-journal-view {
  padding: 2rem;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}
</style>