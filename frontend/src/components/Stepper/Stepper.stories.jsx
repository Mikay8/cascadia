import { useState } from 'react';

import Stepper from './Stepper.jsx';

const RUN_STEPS = ['Period and fund', 'Cash pool', 'Simulate', 'Submit for approval'];

export default {
  title: 'Components/Stepper',
  component: Stepper,
  args: { steps: RUN_STEPS, current: 2 },
};

export const NewRun = { name: 'New run, step 3' };
export const FirstStep = { args: { current: 0 } };

function InteractiveStepper(args) {
  const [current, setCurrent] = useState(args.current);
  return <Stepper {...args} current={current} onStepClick={setCurrent} />;
}

export const Interactive = { render: (args) => <InteractiveStepper {...args} /> };
