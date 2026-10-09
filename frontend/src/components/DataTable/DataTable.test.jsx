import { render, screen, within } from '@testing-library/react';

import DataTable from './DataTable.jsx';

const columns = [
  { key: 'name', header: 'Investor' },
  { key: 'amount', header: 'Amount', align: 'end' },
];

test('renders a row per item under its column headers', () => {
  render(<DataTable columns={columns} rows={[{ id: 1, name: 'First Valley Bank', amount: 'x' }]} />);

  expect(screen.getByRole('columnheader', { name: 'Investor' })).toBeInTheDocument();
  expect(screen.getByRole('cell', { name: 'First Valley Bank' })).toBeInTheDocument();
});

test('shows the empty state when there are no rows', () => {
  render(<DataTable columns={columns} rows={[]} empty="No investors yet" />);

  expect(screen.getByRole('cell', { name: 'No investors yet' })).toBeInTheDocument();
});

test('loading marks the table busy and hides placeholder rows from assistive tech', () => {
  render(<DataTable columns={columns} rows={[]} loading />);

  const table = screen.getByRole('table');
  expect(table).toHaveAttribute('aria-busy', 'true');
  expect(within(table).queryAllByRole('cell')).toHaveLength(0);
});
