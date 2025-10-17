<template>
  <div class="calendar-overlay" v-if="isOpen">
    <div class="calendar-container">
      <h3>Select a day to start your journal</h3>
      <!-- A simple date picker for now -->
      <input type="date" v-model="selectedDate" />
      <div class="calendar-actions">
        <button @click="startDay">Start Day</button>
        <button @click="closeCalendar">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useJournalStore } from '../../stores/journalStore';
import { useRouter } from 'vue-router';

const isOpen = ref(false);
const selectedDate = ref(new Date().toISOString().substr(0, 10));
const journalStore = useJournalStore();
const router = useRouter();

const openCalendar = () => {
  isOpen.value = true;
};

const closeCalendar = () => {
  isOpen.value = false;
};

const startDay = async () => {
  if (selectedDate.value) {
    try {
      await journalStore.startDay(selectedDate.value);
      router.push({ name: 'DailyJournalView', params: { date: selectedDate.value } });
      closeCalendar();
    } catch (error) {
      console.error('Error starting day:', error);
      // Handle error (e.g., show a toast notification)
    }
  }
};

defineExpose({
  openCalendar,
});
</script>

<style scoped>
.calendar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.calendar-container {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
}

.calendar-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
</style>