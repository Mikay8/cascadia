import Button from '../Button/Button.jsx';
import EmptyState from './EmptyState.jsx';

export default {
  title: 'Components/EmptyState',
  component: EmptyState,
};

export const NoRuns = {
  name: 'Empty (no runs yet)',
  args: {
    title: 'No waterfall runs yet',
    children:
      "Each run allocates one period's settled cash across Class A, B and C. You need an active ruleset and at least one settled servicing event first.",
    action: <Button variant="primary">Start first run</Button>,
  },
};

export const PermissionDenied = {
  name: 'Permission denied (direct link)',
  args: {
    title: 'Settings is only available to tenant admins',
    children:
      'You are signed in as Executive on Main Street Opportunity Fund. Ask Alex Chen (tenant admin) if you need access.',
    action: <a href="#dashboard">Back to Dashboard</a>,
  },
};
