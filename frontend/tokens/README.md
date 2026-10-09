# Design tokens

The only place colors, spacing, radius, shadows, and type sizes are defined. Built from `docs/design-handoff/`.

| File | Holds |
| --- | --- |
| `ramp.css` | Base color ramps. **Placeholders** for the Broadsheet design system until its real values are exported. |
| `theme.css` | Cascadia color roles (`--cs-*`) for light, dark, and system mode. |
| `scale.css` | Type scale (staff and investor portal), spacing, radius, focus ring. |
| `base.css` | Body, link, and focus defaults. |
| `index.css` | Imports all of the above plus the Source Serif 4 font. |

Rules:

- Components use roles (`var(--cs-payout)`), never ramp steps (`var(--color-accent-500)`) and never literal values.
- Theme is set with `data-theme="light"` or `"dark"` on `<html>`; with neither, it follows the OS. Shared links and PDF exports always use light.
- The investor portal sets `data-audience="portal"` to step every type size up one level.
- Lint enforces this: ESLint `cascadia/no-hardcoded-colors` for JS, Stylelint for CSS. Files in this folder are exempt.
