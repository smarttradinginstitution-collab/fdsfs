import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import StatCard from '../index.vue';

// Mock del composable useMetricInfo, dato che non è rilevante per il test del componente
vi.mock('../../../../composables/useMetricInfo.js', () => ({
  useMetricInfo: vi.fn(() => ({
    info: { title: 'Test Metric', description: 'A test description.' }
  })),
}));

describe('StatCard/index.vue', () => {
  it('dovrebbe renderizzare correttamente una statistica di base con valore positivo', () => {
    const stat = {
      key: 'netPnl',
      label: 'Net P&L',
      value: '+$1,234.56',
      changeType: 'positive',
    };

    const wrapper = mount(StatCard, {
      props: { stat },
    });

    // Controlla che il label e il valore siano presenti
    expect(wrapper.text()).toContain('Net P&L');
    expect(wrapper.text()).toContain('+$1,234.56');

    // Controlla che la classe per il valore positivo sia applicata
    const valueElement = wrapper.find('.stat-value');
    expect(valueElement.classes()).toContain('stat-value--positive');
    expect(valueElement.classes()).not.toContain('stat-value--negative');
  });

  it('dovrebbe applicare la classe corretta per un valore negativo', () => {
    const stat = {
      key: 'netPnl',
      label: 'Net P&L',
      value: '-$500.00',
      changeType: 'negative',
    };

    const wrapper = mount(StatCard, {
      props: { stat },
    });

    // Controlla che la classe per il valore negativo sia applicata
    const valueElement = wrapper.find('.stat-value');
    expect(valueElement.classes()).toContain('stat-value--negative');
    expect(valueElement.classes()).not.toContain('stat-value--positive');
  });

  it('dovrebbe renderizzare il layout speciale per il Win Rate', () => {
    const stat = {
      key: 'winRate',
      label: 'Win Rate', // Anche se il componente lo sovrascrive, lo passiamo per coerenza
      value: '60%',
      wins: 12,
      losses: 8,
      breakevens: 2,
      changeType: 'neutral',
    };

    const wrapper = mount(StatCard, {
      props: { stat },
      // Stub dei componenti figli per non testare la loro logica interna
      global: {
        stubs: {
          WinLossDonutChart: true,
        },
      },
    });

    // Controlla il label specifico per il win rate
    expect(wrapper.text()).toContain('Win %');
    // Controlla che i badge con vittorie e sconfitte siano renderizzati
    expect(wrapper.find('.badge.win').text()).toBe('12');
    expect(wrapper.find('.badge.loss').text()).toBe('8');
    // Controlla che il componente del grafico sia presente
    expect(wrapper.findComponent({ name: 'WinLossDonutChart' }).exists()).toBe(true);
  });

  it('dovrebbe renderizzare il GaugeChart per il Profit Factor', () => {
    const stat = {
      key: 'profitFactor',
      label: 'Profit Factor',
      value: '1.8',
      changeType: 'neutral',
    };

    const wrapper = mount(StatCard, {
      props: { stat },
      global: {
        stubs: {
          GaugeChart: true,
        },
      },
    });

    // Controlla che il componente del grafico sia presente
    expect(wrapper.findComponent({ name: 'GaugeChart' }).exists()).toBe(true);
  });
});
