# Cascadia decisions

A running log of choices. Claude Code checks it before assuming anything and updates it whenever a choice is made. Never silently decide an open item; stop and ask a human.

**Status values:** `Decided`, `Proposed` (recommended, not yet confirmed), `Open`.

## Decided

| Decision | Choice | Date | Notes |
| --- | --- | --- | --- |
| Back-end stack | Python with Django, Celery for the queue | 2026-10-08 | Chosen over FastAPI for built-in auth, permissions, admin, and migrations |
| Front-end stack | Plain JavaScript with React | 2026-10-08 | TypeScript considered and declined for now |
| Django version | 5.2 LTS (supported to April 2028), not the current 6.1 | 2026-10-08 | Recheck django-tenants support in 1.2; consider 6.2 LTS (April 2027) once it is supported |
| Money handling | `Decimal` and `NUMERIC` only; the API sends money as strings; the front end never computes money | 2026-10-08 | Hard rule in CLAUDE.md |
| Scope of version 1 | Track and report only; no payments, KYC, or accounting sync | 2026-10-08 | Revisit after a real tenant is live |
| AI role | AI drafts, flags, and explains; never approves, executes, or computes allocations or balances | 2026-10-08 | Hard rule in CLAUDE.md |
| Hosting for build and pilot | Railway: project `cascadia`, `staging` environment now; production created in 1.9 with manual deploys | 2026-10-09 | Revisit at the go-live review: stay, move to AWS, or negotiate Railway Enterprise. Plan tier still to confirm |
| Infrastructure stays portable to AWS | Plain Dockerfiles, env-var config, standard Postgres, `$PORT` and `/healthz` on every service, no Railway-only features in code | 2026-10-09 | Rules and the Railway-to-AWS map are in `docs/INFRASTRUCTURE.md`; every infrastructure PR is checked against them |
| Multi-tenancy | Schema-per-tenant in PostgreSQL, via django-tenants | 2026-10-14 | Confirmed in 1.2: Tenant/Domain models in the shared schema, `TenantMainMiddleware` routes by hostname, `TenantSyncRouter` splits migrations |
| Tenant provisioning package | django-tenants 4.0.0 | 2026-10-14 | Verified before 1.2: maintained (now under the django-tenants org), Production/Stable, MIT, classifiers list Django 5.2/6.0/6.1, requires Django >=5.2,<6.2 |
| MFA approach | TOTP via django-otp 1.7 (authenticator apps), no SMS; MFA is per-user (enroll to enable); login is password first, then TOTP challenge; sessions expire after 30 min idle (sliding) and 30 min absolute, enforced server-side | 2026-10-16 | Set in 1.4; confirm the timeout lengths and per-user (not mandatory) MFA in review |

## Proposed

| Decision | Recommendation | Notes |
| --- | --- | --- |
| Toolchain versions | Python 3.12, PostgreSQL 18, Node 22, Vite 8, Vitest 5, ESLint 9, Storybook 10 | Set in 0.4 and 1.8. ESLint 10 waits for eslint-plugin-react support |
| Front-end styling | CSS Modules reading CSS custom properties from `frontend/tokens/`; Stylelint bans literal colors and sizes outside tokens | Set in 1.8. No CSS-in-JS or utility framework |
| Placeholder color ramps | Approximate Broadsheet ramps in `frontend/tokens/ramp.css` until the real Broadsheet styles are exported | Set in 1.8. All text pairs checked at WCAG AA 4.5:1. Swap before design sign-off |
| Extra color roles | `--cs-neutral-tint`, `--cs-loss-strong`, `--cs-on-loss-strong`, `--cs-inverse`, `--cs-on-inverse` | Set in 1.8. The wireframes use these ramp steps directly; designer to confirm or rename |
| Spacing steps 7 and 8 | 60 px and 80 px | Set in 1.8. The style guide names `--space-1` to `-8` but lists only six values |

## Open

These block specific increments. Close them in Phase 0.

| Decision | Blocks | Options and notes |
| --- | --- | --- |
| Rounding rule for allocations, and which class absorbs the remainder | 2.1 | For example largest remainder, with ties to a named class |
| Correction policy for backdated events | 3.7, 2.7 | Restate past runs, or book a correcting entry in the current period (auditors generally prefer the second) |
| Maker-checker approval flow for rulesets and run execution | 1.5, 4.7 | Includes how a CDFI with one finance person satisfies it (outside CPA, board member) |
| Is the fund approver its own role or a permission on fund administrator | 1.5 | See the open questions in `ROLES.md` |
| First servicer to integrate, and whether a sandbox exists | 3.3 | Sandbox payloads must be in hand before 3.3 starts |
| Loss-absorption order versus payout order for the first partner | 2.2, 2.5 | Often the reverse of each other; confirm from the partner's agreements |
| Whether accrued returns are paid out on a schedule or only credited to capital accounts | 2.4 | Affects tier definitions and statements |
| Can executives see investor names and balances, or only fund totals | 4.6 | Wireframe both variants |
| Whether AI-drafted rulesets go ahead | 4.11 | Decide from the 0.5 experiment results |
