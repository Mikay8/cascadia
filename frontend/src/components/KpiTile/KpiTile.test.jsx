import { render, screen } from '@testing-library/react';

import KpiTile from './KpiTile.jsx';

test('shows the formatted figure and its label', () => {
  render(<KpiTile label="Cash ready to distribute" value="412350.00" />);

  expect(screen.getByText('Cash ready to distribute')).toBeInTheDocument();
  expect(screen.getByText('$412,350.00')).toBeInTheDocument();
});

test('loading shows the label but no figure', () => {
  render(<KpiTile label="Cash ready to distribute" value="412350.00" loading />);

  expect(screen.getByLabelText('Cash ready to distribute, loading')).toHaveAttribute(
    'aria-busy',
    'true',
  );
  expect(screen.queryByText('$412,350.00')).not.toBeInTheDocument();
});
