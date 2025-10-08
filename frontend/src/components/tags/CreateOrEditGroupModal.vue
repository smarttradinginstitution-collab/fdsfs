<script setup>
import { ref, watch, computed } from "vue";
import { useTagsStore } from "@/stores/tagsStore";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps({
  modelValue: { // for v-model
    type: Boolean,
    required: true,
  },
  group: { // The group to edit, if any
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["update:modelValue"]);

const tagsStore = useTagsStore();
const form = ref({ name_group: "" });
const isLoading = ref(false);
const errorMessage = ref("");

const isEditing = computed(() => !!props.group);
const modalTitle = computed(() => isEditing.value ? "Edit Group" : "Create New Group");

// When the modal opens, populate the form if we are editing
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    form.value.name_group = props.group ? props.group.name_group : "";
    errorMessage.value = "";
    isLoading.value = false;
  }
});

const closeModal = () => {
  emit("update:modelValue", false);
};

const handleSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    if (isEditing.value) {
      await tagsStore.updateTagGroup(props.group.id, form.value);
    } else {
      await tagsStore.createTagGroup(form.value);
    }
    closeModal();
  } catch (error) {
    errorMessage.value = "An error occurred. Please try again.";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <BaseModal :show="modelValue" @close="closeModal">
    <template #title>{{ modalTitle }}</template>
    <template #content>
      <form @submit.prevent="handleSubmit">
        <BaseInput
          v-model="form.name_group"
          label="Group Name"
          placeholder="e.g., Market Conditions"
          required
        />
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </template>
    <template #actions>
      <BaseButton @click="closeModal" variant="secondary">Cancel</BaseButton>
      <BaseButton @click="handleSubmit" variant="primary" :disabled="isLoading">
        {{ isLoading ? "Saving..." : "Save" }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style lang="scss" scoped>
.error-message {
  color: var(--semantic-color-text-danger);
  font-size: var(--semantic-font-size-body-sm);
  margin-top: 8px;
}
</style>