import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import TradeLabelManager from '../TradeLabelManager.vue';
import IconButton from '../../ui/IconButton.vue';

describe('TradeLabelManager.vue', () => {
  const mockTrade = {
    id: '1',
    mistakes: [],
  };

  it('renders the IconButton with the correct aria-label', () => {
    const wrapper = mount(TradeLabelManager, {
      props: {
        trade: mockTrade,
        labelType: 'mistakes',
        title: 'Mistakes',
      },
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              labels: {
                labels: {
                  mistakes: [{ id: '1', name: 'FOMO' }],
                },
              },
            },
          }),
        ],
      },
    });

    const iconButton = wrapper.findComponent(IconButton);
    expect(iconButton.exists()).toBe(true);
    expect(iconButton.attributes('aria-label')).toBe('Add new Mistakes');
  });
});
