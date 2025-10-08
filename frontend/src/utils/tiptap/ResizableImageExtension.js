import { Node } from '@tiptap/core';
import { VueNodeViewRenderer } from '@tiptap/vue-3';
import ResizableImage from '@/components/notebook/ResizableImage.vue';

// This is a custom node that replaces the default Tiptap image extension.
// It is built from scratch to have full control over its behavior,
// especially drag-and-drop, to prevent the duplication bug.
export const ResizableImageExtension = Node.create({
  name: 'resizable-image', // Must match the name used in the editor setup

  // This makes it a block-level node, which is better for images
  group: 'block',

  // This makes the node draggable
  draggable: true,

  // An atomic node is treated as a single, indivisible unit.
  atom: true,

  // Define the attributes (data) that this node will store
  addAttributes() {
    return {
      src: {
        default: null,
      },
      width: {
        default: '100%',
      },
      height: {
        default: 'auto',
      },
      alt: {
        default: null,
      },
    };
  },

  // How to parse the node from HTML content
  parseHTML() {
    return [
      {
        tag: 'img[src]',
        getAttrs: dom => ({
          src: dom.getAttribute('src'),
          alt: dom.getAttribute('alt'),
          width: dom.getAttribute('width') || '100%',
          height: dom.getAttribute('height') || 'auto',
        }),
      },
    ];
  },

  // How to render the node back to HTML
  renderHTML({ HTMLAttributes }) {
    // The Vue component will handle the rendering, but this is a fallback
    return ['img', HTMLAttributes];
  },

  // How to render the node in the editor (using our Vue component)
  addNodeView() {
    return VueNodeViewRenderer(ResizableImage);
  },

  // Add custom commands for this node
  addCommands() {
    return {
      setResizableImage: (options) => ({ commands }) => {
        return commands.insertContent({
          type: this.name,
          attrs: options,
        });
      },
    };
  },
});