import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ThemeToggle from '../ThemeToggle.vue';
import { useUiStore } from '../../../stores/uiStore';

describe('ThemeToggle.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    // Resetta l'attributo sul document per ogni test
    document.documentElement.removeAttribute('data-theme');
  });

  it('dovrebbe cambiare il tema da light a dark al click', async () => {
    const uiStore = useUiStore();
    // Stato iniziale
    expect(uiStore.theme).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');

    const wrapper = mount(ThemeToggle);
    await wrapper.find('button').trigger('click');

    // Stato finale
    expect(uiStore.theme).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
