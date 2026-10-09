# Front end

React app built with Vite. The root `CLAUDE.md` hard rules apply here first; above all, the front end never does money math. It formats money strings it receives from the API.

## Layout

```
tokens/            design tokens; the only place colors, spacing, and type sizes are defined (see its README)
src/components/    design-system components, one folder each: Name.jsx, Name.module.css, Name.stories.jsx, Name.test.jsx
src/components/index.js   the public list of components; screens import from here
src/lib/money.js   formatMoney: formats API money strings without converting to numbers
src/screens/       one folder per screen
eslint-rules/      local lint rules, including no-hardcoded-colors
.storybook/        Storybook config, with a Light/Dark toolbar switch
```

## Commands

Run from `frontend/` with Node 22.

```
npm install
npm run dev               # Vite dev server; /api is proxied to Django on :8000
npm test                  # Vitest
npm run lint              # ESLint (no-hardcoded-colors) and Stylelint (no literal colors or sizes in CSS)
npm run build
npm run storybook         # component library on http://localhost:6006
npm run build-storybook   # static build; CI runs it
```

## Conventions

- Plain JavaScript (decided in `docs/DECISIONS.md`), with JSX in `.jsx` files.
- Style with CSS Modules that read `--cs-*` roles and `--space-*`, `--radius-*`, `--cs-type-*` scales. Never read ramp steps (`--color-*`) outside `tokens/`.
- Use design-system components; do not restyle them locally.
- Status is never shown by color alone; use `StatusBadge`, and add new statuses to its `statuses.js`.
- Show money with `Money` or `formatMoney`. Never `Number()`, `parseFloat()`, or arithmetic on money.
- An action the user may not take stays visible, disabled, with `disabledReason`.
- Every component has stories for its default, empty, and loading states where they apply.
