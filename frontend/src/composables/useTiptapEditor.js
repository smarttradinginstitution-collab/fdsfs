
import { useEditor } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import TextAlign from '@tiptap/extension-text-align';
import FontFamily from '@tiptap/extension-font-family';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import Highlight from '@tiptap/extension-highlight';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { FontSize } from '@/utils/tiptap/FontSize.js';
import { ResizableImageExtension } from '@/utils/tiptap/ResizableImageExtension.js';

export function useTiptapEditor(content) {
  const editor = useEditor({
    content: content,
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3, 4, 5, 6] },
        link: { openOnClick: false },
      }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      FontFamily,
      TextStyle,
      Color,
      Highlight.configure({ multicolor: true }),
      TaskList,
      TaskItem.configure({ nested: true }),
      FontSize,
      ResizableImageExtension,
    ],
    editorProps: {
      attributes: { class: 'prose prose-invert focus:outline-none' },
    },
  });

  return { editor };
}
