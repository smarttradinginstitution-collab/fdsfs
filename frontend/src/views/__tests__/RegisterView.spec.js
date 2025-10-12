import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import RegisterView from '../RegisterView.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
  })),
  createRouter: vi.fn(() => ({
    beforeEach: vi.fn(),
  })),
  createWebHistory: vi.fn(),
}));

// Mock il componente BaseInput per semplicità
const BaseInput = {
  template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  props: ['modelValue'],
};

// Mock il componente BaseButton
const BaseButton = {
  template: '<button><slot/></button>',
};

describe('RegisterView.vue', () => {
  let pinia;
  let router;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    router = { push: vi.fn() };
    useRouter.mockReturnValue(router);
  });

  it('should call auth store register action and redirect on successful registration', async () => {
    const authStore = useAuthStore();
    // Spy sull'azione register
    const registerSpy = vi.spyOn(authStore, 'register').mockResolvedValue();

    const wrapper = mount(RegisterView, {
      global: {
        plugins: [pinia],
        stubs: {
            BaseInput,
            BaseButton,
            'router-link': false // Per evitare warning
        }
      },
    });

    // Simula l'input dell'utente
    await wrapper.find('input[type="text"]').setValue('Test User');
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    const passwordInputs = wrapper.findAll('input[type="password"]');
    await passwordInputs[0].setValue('password123');
    await passwordInputs[1].setValue('password123');

    // Simula il submit del form
    await wrapper.find('form').trigger('submit.prevent');

    // Verifica che l'azione register sia stata chiamata
    expect(registerSpy).toHaveBeenCalledTimes(1);
    expect(registerSpy).toHaveBeenCalledWith('Test User', 'test@example.com', 'password123', 'password123');

    // Verifica che il router.push sia stato chiamato per il redirect
    expect(router.push).toHaveBeenCalledTimes(1);
    expect(router.push).toHaveBeenCalledWith({ name: 'login', query: { registered: 'true' } });
  });

  it('should show an error message if passwords do not match', async () => {
    const wrapper = mount(RegisterView, {
        global: {
          plugins: [pinia],
          stubs: {
              BaseInput,
              BaseButton,
              'router-link': false
          }
        },
      });

    // Simula l'input con password non corrispondenti
    await wrapper.find('input[type="password"]').setValue('password123');
    await wrapper.findAll('input[type="password"]')[1].setValue('password456');

    // Simula il submit del form
    await wrapper.find('form').trigger('submit.prevent');

    // Verifica che il messaggio di errore sia mostrato
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Le password non corrispondono.');
  });
});