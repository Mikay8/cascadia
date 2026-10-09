import { fireEvent, render, screen } from '@testing-library/react';

import Stepper from './Stepper.jsx';

const steps = ['Period and fund', 'Cash pool', 'Simulate', 'Submit'];

test('only completed steps are clickable', () => {
  const onStepClick = vi.fn();
  render(<Stepper steps={steps} current={2} onStepClick={onStepClick} />);

  expect(screen.getAllByRole('button')).toHaveLength(2);
  fireEvent.click(screen.getByRole('button', { name: /Cash pool/ }));
  expect(onStepClick).toHaveBeenCalledWith(1);
});

test('marks the current step for assistive tech', () => {
  render(<Stepper steps={steps} current={2} />);

  expect(screen.getByText('3 Simulate')).toHaveAttribute('aria-current', 'step');
});
