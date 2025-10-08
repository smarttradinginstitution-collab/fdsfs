<script setup>
import { ref, watch, computed } from "vue";
import { useTagsStore } from "@/stores/tagsStore";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ColorSelector from "@/components/ui/ColorSelector.vue";

const props = defineProps({
  modelValue: { // for v-model
    type: Boolean,
    required: true,
  },
  tag: { // The tag to edit, if any
    type: Object,
    default: null,
  },
  groupId: { // The ID of the group to add the tag to
    type: String,
    required: true,
  }
});

const emit = defineEmits(["update:modelValue"]);

const tagsStore = useTagsStore();
const form = ref({
  name_tag: "",
  color: "#4ade80", // Default to a nice green
  tags_group_id: props.groupId,
});
const isLoading = ref(false);
const errorMessage = ref("");

const isEditing = computed(() => !!props.tag);
const modalTitle = computed(() => isEditing.value ? "Edit Tag" : "Create New Tag");

// When the modal opens, populate the form
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    form.value.name_tag = props.tag ? props.tag.name_tag : "";
    form.value.color = props.tag ? props.tag.color : "#4ade80";
    form.value.tags_group_id = props.groupId;
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
      await tagsStore.updateTag(props.tag.id, form.value);
    } else {
      await tagsStore.createTag(form.value);
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
  <BaseModal :model-value="modelValue" @update:model-value="closeModal">
    <template #title>{{ modalTitle }}</template>
    <template #content>
      <form @submit.prevent="handleSubmit" class="tag-form">
        <BaseInput
          v-model="form.name_tag"
          label="Tag Name"
          placeholder="e.g., Breakout Strategy"
          required
        />
        <ColorSelector v-model="form.color" />
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
.tag-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.error-message {
  color: var(--semantic-color-text-danger);
  font-size: var(--semantic-font-size-body-sm);
  margin-top: 8px;
}
</style>