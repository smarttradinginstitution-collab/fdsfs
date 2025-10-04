<template>
  <div v-if="editor" class="tiptap-toolbar">
    <div class="toolbar-section">
      <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">
        <IconBold />
      </button>
      <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }">
        <IconItalic />
      </button>
      <button @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }">
        <IconUnderline />
      </button>
      <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }">
        <IconStrikethrough />
      </button>
    </div>
    <div class="divider"></div>
    <div class="toolbar-section">
      <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }">
        H1
      </button>
      <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
        H2
      </button>
      <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }">
        <IconListUl />
      </button>
      <button @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }">
        <IconListOl />
      </button>
    </div>
     <div class="divider"></div>
    <div class="toolbar-section">
        <button @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }">
            <IconAlignLeft />
        </button>
        <button @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }">
            <IconAlignCenter />
        </button>
        <button @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }">
            <IconAlignRight />
        </button>
    </div>
  </div>
</template>

<script setup>
import IconBold from '@/components/icons/IconBold.vue';
import IconItalic from '@/components/icons/IconItalic.vue';
import IconUnderline from '@/components/icons/IconUnderline.vue';
import IconStrikethrough from '@/components/icons/IconStrikethrough.vue';
import IconListUl from '@/components/icons/IconListUl.vue';
import IconListOl from '@/components/icons/IconListOl.vue';
import IconAlignLeft from '@/components/icons/IconAlignLeft.vue';
import IconAlignCenter from '@/components/icons/IconAlignCenter.vue';
import IconAlignRight from '@/components/icons/IconAlignRight.vue';

defineProps({
  editor: {
    type: Object,
    required: true,
  },
});
</script>

<style lang="scss" scoped>
.tiptap-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: var(--fluid-spacing-s);
  border-bottom: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-secondary);
}

.toolbar-section {
  display: flex;
  align-items: center;

  button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    cursor: pointer;
    color: var(--semantic-color-text-secondary);
    border-radius: var(--semantic-border-radius-interactive);

    &:hover {
      background-color: var(--semantic-color-surface-tertiary);
      color: var(--semantic-color-text-primary);
    }

    &.is-active {
      background-color: var(--semantic-color-interactive-primary-default);
      color: var(--semantic-color-text-on-primary);
    }

    svg {
      width: 20px;
      height: 20px;
    }
  }
}

.divider {
  width: 1px;
  height: 24px;
  background-color: var(--semantic-color-border-default);
  margin: 0 var(--fluid-spacing-s);
}
</style>