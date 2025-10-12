<script setup>
import { ref, watch } from 'vue';
import { useImageStore } from '../../stores/imageStore';
import BaseModal from '../ui/BaseModal.vue';
import BaseButton from '../ui/BaseButton.vue';
import BaseInput from '../ui/BaseInput.vue';
import BaseTextarea from '../ui/BaseTextarea.vue';

const props = defineProps({
  show: Boolean,
  image: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close']);

const imageStore = useImageStore();
const localImage = ref({});

const imagePhases = ['Pre-Entrata', 'Entrata', 'Gestione', 'Uscita', 'Post-Analisi'];
const imageCategories = ['Analisi Tecnica', 'Analisi Fondamentale', 'News', 'Psicologia', 'Altro'];

watch(() => props.image, (newImage) => {
  if (newImage) {
    localImage.value = { ...newImage };
  } else {
    localImage.value = {};
  }
}, { immediate: true });

const saveChanges = async () => {
  if (!localImage.value.id) return;

  const updateData = {
    description: localImage.value.description,
    category: localImage.value.category,
    phase: localImage.value.phase,
    is_primary_before: localImage.value.is_primary_before,
    is_primary_after: localImage.value.is_primary_after,
  };

  await imageStore.updateImageMetadata(localImage.value.id, updateData);
  emit('close');
};

const closeModal = () => {
  emit('close');
};
</script>

<template>
  <BaseModal :show="show" @close="closeModal" title="Edit Image Details">
    <div v-if="localImage" class="edit-form">
      <img :src="localImage.url" class="preview-image" />

      <BaseTextarea
        v-model="localImage.description"
        label="Description"
        placeholder="e.g., Chart showing breakout confirmation"
      />

      <div class="form-row">
        <div class="form-group">
          <label for="category">Category</label>
          <select id="category" v-model="localImage.category">
            <option disabled value="">Please select one</option>
            <option v-for="cat in imageCategories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="phase">Trade Phase</label>
          <select id="phase" v-model="localImage.phase">
            <option disabled value="">Please select one</option>
            <option v-for="p in imagePhases" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="checkbox-group">
          <input type="checkbox" id="is_primary_before" v-model="localImage.is_primary_before" />
          <label for="is_primary_before">Set as Primary "Before" Chart</label>
        </div>
        <div class="checkbox-group">
          <input type="checkbox" id="is_primary_after" v-model="localImage.is_primary_after" />
          <label for="is_primary_after">Set as Primary "After" Chart</label>
        </div>
      </div>

    </div>
    <template #footer>
      <BaseButton @click="closeModal" variant="secondary">Cancel</BaseButton>
      <BaseButton @click="saveChanges" variant="primary">Save Changes</BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped lang="scss">
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: var(--semantic-border-radius-container);
  background-color: var(--semantic-color-surface-secondary);
}

.form-row {
  display: flex;
  gap: 1rem;

  > .form-group, > .checkbox-group {
    flex: 1;
  }
}

.form-group, .checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label {
    font: var(--semantic-font-style-label-md);
    color: var(--semantic-color-text-secondary);
  }

  select, input {
    width: 100%;
  }
}

.checkbox-group {
  flex-direction: row;
  align-items: center;

  input[type="checkbox"] {
    width: auto;
    margin-right: 0.5rem;
  }
}
</style>