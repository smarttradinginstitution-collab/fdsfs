import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseButton from '../ui/BaseButton.vue';

describe('Ambiente di Test', () => {
  it('dovrebbe montare un componente Vue senza errori', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Test Button' }
    });
    expect(wrapper.text()).toContain('Test Button');
  });
});
