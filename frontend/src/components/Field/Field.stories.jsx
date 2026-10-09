import Field from './Field.jsx';

export default {
  title: 'Components/Field',
  component: Field,
  decorators: [
    (Story) => (
      <div style={{ maxWidth: '360px' }}>
        <Story />
      </div>
    ),
  ],
  args: { label: 'Effective date', defaultValue: 'Oct 1, 2026' },
};

export const Default = {};
export const Empty = { args: { defaultValue: undefined, placeholder: 'Choose a date' } };
export const WithHint = { args: { label: 'Sample cash amount', defaultValue: '60000.00', hint: 'Used for simulation only.' } };
export const WithError = {
  args: { label: 'Tier 3 rate', defaultValue: '30.00%', error: 'Rates must be between 0% and 25%.' },
};
export const Multiline = {
  name: 'Comment (textarea)',
  args: {
    label: 'Comment (required to reject)',
    defaultValue: undefined,
    multiline: true,
    rows: 4,
    placeholder: 'Explain what needs to change',
  },
};
export const Disabled = { args: { disabled: true } };
