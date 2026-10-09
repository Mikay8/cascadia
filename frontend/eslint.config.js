import js from '@eslint/js';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import storybook from 'eslint-plugin-storybook';
import globals from 'globals';

import noHardcodedColors from './eslint-rules/no-hardcoded-colors.js';

export default [
  { ignores: ['dist', 'coverage', 'storybook-static', '!.storybook'] },
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: { ...globals.browser, ...globals.node, ...globals.vitest },
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    settings: { react: { version: 'detect' } },
    plugins: {
      react,
      'react-hooks': reactHooks,
      cascadia: { rules: { 'no-hardcoded-colors': noHardcodedColors } },
    },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      'react/prop-types': 'off',
      'cascadia/no-hardcoded-colors': 'error',
    },
  },
  ...storybook.configs['flat/recommended'],
  {
    files: ['tokens/**', 'eslint-rules/**'],
    rules: { 'cascadia/no-hardcoded-colors': 'off' },
  },
];
