import { render, screen } from '@testing-library/react';

import Money from './Money.jsx';

test('negatives use parentheses and read as minus', () => {
  render(<Money value="-9200.00" />);

  expect(screen.getByText('($9,200.00)')).toHaveAttribute('aria-hidden', 'true');
  expect(screen.getByText('minus $9,200.00')).toBeInTheDocument();
});

test('not applicable shows None', () => {
  render(<Money value={null} />);

  expect(screen.getByText('None')).toBeInTheDocument();
});
