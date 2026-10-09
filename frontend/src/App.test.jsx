import { render, screen } from '@testing-library/react';

import App from './App.jsx';

test('renders the app name', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: 'Cascadia' })).toBeInTheDocument();
});
