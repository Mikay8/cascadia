import { render, screen } from '@testing-library/react';

import Button from './Button.jsx';

test('a disabled action stays visible and explains why', () => {
  render(
    <Button variant="primary" disabled disabledReason="You submitted this change.">
      Approve
    </Button>,
  );

  const button = screen.getByRole('button', { name: 'Approve' });
  expect(button).toBeDisabled();
  expect(button).toHaveAccessibleDescription('You submitted this change.');
});

test('busy disables the button and marks it busy', () => {
  render(<Button busy>Execute run</Button>);

  const button = screen.getByRole('button', { name: 'Execute run' });
  expect(button).toBeDisabled();
  expect(button).toHaveAttribute('aria-busy', 'true');
});
