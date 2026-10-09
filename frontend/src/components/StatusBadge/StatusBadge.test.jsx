import { render, screen } from '@testing-library/react';

import StatusBadge from './StatusBadge.jsx';
import { STATUSES } from './statuses.js';

test('every status has a word, so it never relies on color', () => {
  for (const family of Object.values(STATUSES)) {
    for (const status of Object.values(family)) {
      expect(status.label).toMatch(/\w/);
    }
  }
});

test('renders the glyph as decoration and the word as text', () => {
  render(<StatusBadge family="run" status="failed" />);

  expect(screen.getByText('Failed')).toBeInTheDocument();
  expect(screen.getByText('✕')).toHaveAttribute('aria-hidden', 'true');
});

test('shows an unknown status plainly and reports it', () => {
  const error = vi.spyOn(console, 'error').mockImplementation(() => {});
  render(<StatusBadge family="run" status="archived" />);

  expect(screen.getByText(/archived/)).toBeInTheDocument();
  expect(error).toHaveBeenCalledOnce();
  error.mockRestore();
});
