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

## Proposed

| Decision | Recommendation | Notes |
| --- | --- | --- |
| Toolchain versions | Python 3.12, PostgreSQL 17, Node 22, Vite 8, Vitest 5, ESLint 9 | Set in 0.4. ESLint 10 waits for eslint-plugin-react support |
| Multi-tenancy | Schema-per-tenant in PostgreSQL | Confirm before increment 1.2; expensive to change later |
| Tenant provisioning package | django-tenants | Verify it is maintained and supports the Django and Postgres versions in use before 1.2 |
| Hosting for build and pilot | Railway Pro, with staging and production environments | Revisit at the go-live review: stay, move to AWS, or negotiate Railway Enterprise. Stay containerized and avoid Railway-specific features |

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
