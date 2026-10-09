import Money from './Money.jsx';

export default {
  title: 'Components/Money',
  component: Money,
  args: { value: '412350.00' },
  argTypes: { size: { control: 'inline-radio', options: ['body', 'kpi'] } },
};

export const Positive = {};
export const Negative = { args: { value: '-9200.00' } };
export const Zero = { args: { value: '0.00' } };
export const NotApplicable = { name: 'Not applicable (empty)', args: { value: null } };
export const Kpi = { args: { size: 'kpi' } };

export const MoneyRule = {
  name: 'Money rule',
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'auto auto',
        gap: 'var(--space-1) var(--space-4)',
        justifyContent: 'start',
      }}
    >
      <span>Positive</span>
      <span style={{ textAlign: 'right' }}>
        <Money value="412350.00" />
      </span>
      <span>Negative</span>
      <span style={{ textAlign: 'right' }}>
        <Money value="-9200.00" />
      </span>
      <span>Zero</span>
      <span style={{ textAlign: 'right' }}>
        <Money value="0.00" />
      </span>
      <span>Not applicable</span>
      <span style={{ textAlign: 'right' }}>
        <Money value={null} />
      </span>
    </div>
  ),
};
