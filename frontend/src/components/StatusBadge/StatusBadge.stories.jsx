import StatusBadge from './StatusBadge.jsx';
import { FAMILIES, STATUSES } from './statuses.js';

export default {
  title: 'Components/StatusBadge',
  component: StatusBadge,
  args: { family: 'run', status: 'executed' },
  argTypes: { family: { control: 'select', options: FAMILIES } },
};

export const Single = {};

export const AllFamilies = {
  name: 'All families',
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
      {FAMILIES.map((family) => (
        <div key={family} style={{ display: 'grid', gap: 'var(--space-1)' }}>
          <span style={{ textTransform: 'uppercase', fontSize: 'var(--cs-type-overline-size)' }}>
            {family}
          </span>
          <span style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-1)' }}>
            {Object.keys(STATUSES[family]).map((status) => (
              <StatusBadge key={status} family={family} status={status} />
            ))}
          </span>
        </div>
      ))}
    </div>
  ),
};

export const UnknownStatus = {
  name: 'Unknown status (API mismatch)',
  args: { family: 'run', status: 'archived' },
};
