import Button from './Button.jsx';

export default {
  title: 'Components/Button',
  component: Button,
  args: { children: 'Submit for approval', variant: 'primary' },
  argTypes: { variant: { control: 'inline-radio', options: ['primary', 'secondary', 'ghost'] } },
};

export const Primary = {};
export const Secondary = { args: { variant: 'secondary', children: 'Export CSV' } };
export const Ghost = { args: { variant: 'ghost', children: 'Discard draft' } };

export const DisabledWithReason = {
  name: 'Disabled with reason (own-work rule)',
  args: {
    children: 'Approve',
    disabled: true,
    disabledReason: 'You submitted this change. Another approver must review it.',
  },
};

export const Loading = { args: { busy: true, children: 'Executing run' } };

export const ActionRow = {
  render: () => (
    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
      <Button variant="secondary">Back</Button>
      <Button variant="ghost">Download snapshot (CSV)</Button>
      <Button variant="primary">Continue to simulate</Button>
    </div>
  ),
};
