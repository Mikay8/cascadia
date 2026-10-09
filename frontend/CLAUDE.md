# Front end

React app built with Vite. The root `CLAUDE.md` hard rules apply here first; above all, the front end never does money math. It formats money strings it receives from the API.

## Layout

```
tokens/            design tokens (increment 1.8); the only place colors, spacing, and type sizes are defined
src/components/    shared design-system components, each with a Storybook story
src/screens/       one folder per screen
eslint-rules/      local lint rules, including no-hardcoded-colors
```

## Commands

Run from `frontend/` with Node 22.

```
npm install
npm run dev        # Vite dev server; /api is proxied to Django on :8000
npm test           # Vitest
npm run lint       # ESLint, including cascadia/no-hardcoded-colors
npm run build
```

Storybook is added in increment 1.8.

## Conventions

- Plain JavaScript (decided in `docs/DECISIONS.md`), with JSX in `.jsx` files.
- Use design-system components; do not restyle them locally.
- Status is never shown by color alone; use the shared status badge.
