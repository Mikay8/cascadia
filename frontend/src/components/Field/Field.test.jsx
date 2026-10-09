import { render, screen } from '@testing-library/react';

import Field from './Field.jsx';

test('the label names the control', () => {
  render(<Field label="Effective date" />);

  expect(screen.getByRole('textbox', { name: 'Effective date' })).toBeInTheDocument();
});

test('errors are announced with the control and do not rely on color', () => {
  render(<Field label="Tier 3 rate" hint="Annual rate" error="Rates must be between 0% and 25%." />);

  const input = screen.getByRole('textbox', { name: 'Tier 3 rate' });
  expect(input).toBeInvalid();
  expect(input).toHaveAccessibleDescription('Annual rate Rates must be between 0% and 25%.');
  expect(screen.getByText('▲')).toHaveAttribute('aria-hidden', 'true');
});

test('multiline renders a textarea', () => {
  render(<Field label="Comment" multiline />);

  expect(screen.getByRole('textbox', { name: 'Comment' }).tagName).toBe('TEXTAREA');
});
