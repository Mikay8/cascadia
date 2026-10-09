import KpiTile from './KpiTile.jsx';

export default {
  title: 'Components/KpiTile',
  component: KpiTile,
  decorators: [
    (Story) => (
      <div style={{ maxWidth: '360px' }}>
        <Story />
      </div>
    ),
  ],
  args: {
    label: 'Cash ready to distribute',
    value: '412350.00',
    caption: 'Settled, Q3 2026 · as of Sep 30',
    action: <a href="#calc">Show calculation</a>,
  },
};

export const Default = {};
export const Loading = { args: { loading: true } };
export const NotApplicable = { name: 'Empty (not applicable)', args: { value: null, action: null } };
export const Negative = { args: { label: 'Net change', value: '-9200.00', action: null } };
