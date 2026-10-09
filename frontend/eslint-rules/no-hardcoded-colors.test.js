import { RuleTester } from 'eslint';

import rule from './no-hardcoded-colors.js';

// RuleTester registers its own describe/it blocks through the vitest globals.
const tester = new RuleTester({
  languageOptions: { parserOptions: { ecmaFeatures: { jsx: true } } },
});

tester.run('no-hardcoded-colors', rule, {
  valid: [
    "const c = 'var(--color-ink)';",
    "const id = '#section-2';",
    'const s = <div style={{ color: tokens.ink }} />;',
  ],
  invalid: [
    { code: "const c = '#0af';", errors: [{ messageId: 'hardcoded' }] },
    { code: "const c = '#00aaff';", errors: [{ messageId: 'hardcoded' }] },
    { code: "const c = 'rgba(0, 0, 0, 0.5)';", errors: [{ messageId: 'hardcoded' }] },
    { code: 'const c = `hsl(${h}, 50%, 50%)`;', errors: [{ messageId: 'hardcoded' }] },
    { code: "const s = <div style={{ color: '#fff' }} />;", errors: [{ messageId: 'hardcoded' }] },
  ],
});
