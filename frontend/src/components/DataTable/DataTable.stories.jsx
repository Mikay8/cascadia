import Button from '../Button/Button.jsx';
import EmptyState from '../EmptyState/EmptyState.jsx';
import Money from '../Money/Money.jsx';
import StatusBadge from '../StatusBadge/StatusBadge.jsx';
import DataTable from './DataTable.jsx';

const columns = [
  { key: 'period', header: 'Period' },
  { key: 'status', header: 'Status', render: (row) => <StatusBadge family="run" status={row.status} /> },
  { key: 'cashPool', header: 'Cash pool', align: 'end', render: (row) => <Money value={row.cashPool} /> },
  { key: 'distributed', header: 'Distributed', align: 'end', render: (row) => <Money value={row.distributed} /> },
  { key: 'ruleset', header: 'Ruleset' },
  { key: 'executed', header: 'Executed', render: (row) => row.executed ?? 'None' },
  { key: 'actions', header: 'Actions', align: 'end', render: () => <a href="#history">History</a> },
];

// Mock data. Money is strings, exactly as the API sends it.
const rows = [
  { id: 1, period: 'Q3 2026', status: 'pendingApproval', cashPool: '412350.00', distributed: '95000.00', ruleset: 'v4' },
  { id: 2, period: 'Q2 2026', status: 'executed', cashPool: '398120.40', distributed: '95000.00', ruleset: 'v4', executed: 'Jul 8, 2026' },
  { id: 3, period: 'Q1 2026', status: 'executed', cashPool: '385006.15', distributed: '95000.00', ruleset: 'v4', executed: 'Apr 9, 2026' },
  { id: 4, period: 'Q4 2025 · run 2', status: 'executed', cashPool: '371880.00', distributed: '95000.00', ruleset: 'v3', executed: 'Jan 14, 2026' },
  { id: 5, period: 'Q4 2025 · run 1', status: 'failed', cashPool: '371880.00', distributed: '0.00', ruleset: 'v3' },
];

export default {
  title: 'Components/DataTable',
  component: DataTable,
  args: { caption: 'Waterfall runs', columns, rows },
};

export const Default = {};
export const Loading = { args: { loading: true } };

export const Empty = {
  args: {
    rows: [],
    empty: (
      <EmptyState title="No waterfall runs yet" action={<Button variant="primary">Start first run</Button>}>
        You need an active ruleset and at least one settled servicing event first.
      </EmptyState>
    ),
  },
};
