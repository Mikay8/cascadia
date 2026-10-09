import '../tokens/index.css';

import { withThemeByDataAttribute } from '@storybook/addon-themes';

/** @type { import('@storybook/react-vite').Preview } */
const preview = {
  decorators: [
    withThemeByDataAttribute({
      themes: { light: 'light', dark: 'dark' },
      defaultTheme: 'light',
      attributeName: 'data-theme',
    }),
  ],
  parameters: {
    layout: 'padded',
    backgrounds: { disable: true },
    a11y: { test: 'error' },
    options: { storySort: { order: ['Foundations', 'Components'] } },
  },
};

export default preview;
