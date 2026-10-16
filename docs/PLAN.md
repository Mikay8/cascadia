# Cascadia build plan

This is the working plan. Claude Code reads it before each session and updates it in every pull request. The stakeholder version lives in the Cascadia doc; if the two disagree, fix this file and then the doc.

**How to use it**
- One increment is one branch and one pull request. Title it `[ID] Name`.
- Do not start an increment until its dependencies are `Done` and any decision it needs is closed in `DECISIONS.md`.
- Update the Status and PR columns in the same pull request that does the work.
- Status values: `Todo`, `In progress`, `In review`, `Done`, `Blocked`.
- Size is a rough effort estimate, not a date: S is one pull request, M is two to four, L is five or more.
- A human reviews every pull request and signs off each phase gate. Phase 0 is mostly human work.

**AI rule across all phases:** AI drafts, flags, and explains. It never approves, executes, or computes allocations or balances.

---

## Phase 0: Validate and decide

**Goal:** confirm the need with real customers and lock the decisions that are costly to change later.
**Depends on:** nothing.
**Gate:** three or more real waterfalls in hand as test cases.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | Calculation prototype: a script that applies the partner's class terms to one past period | Partner's class terms and one period of payments | Output matches the distribution they actually paid, to the cent | S | Todo | |
| 0.2 | Golden-case library: past runs converted to fixtures with inputs and expected outputs | 0.1 | Three or more cases are checked into `golden-cases/` | S | Todo | |
| 0.3 | Clickable UI prototype of capital stack configuration and run detail, on mock data | Design handoff | The partner has walked through it and given feedback | M | Todo | |
| 0.4 | Repo skeleton: structure, CLAUDE.md, lint, test runner, CI | Stack decided (Django) | CI passes on the empty project | S | In review | [#1](https://github.com/Mikay8/cascadia/pull/1) |
| 0.5 | AI ruleset drafting experiment: a script that sends the agreement to a model and compares its draft with a human-built ruleset | 0.2, the partner's agreement | A written comparison logs every difference and the accuracy | S | Todo | |

Human-only work in this phase: customer interviews, the partner's data and agreements, checking the model provider's data-retention and tenant opt-out terms before sending any partner document, and closing the open decisions.

---

## Phase 1: Foundation

**Goal:** a secure, tenant-isolated skeleton with the shared UI components, so later phases only add features.
**Depends on:** Phase 0 decisions.
**Gate:** cross-tenant leak tests pass.
**Parallel work:** 1.8 (design system) runs in its own branch alongside 1.2 to 1.7.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Docker setup and a staging environment on Railway | 0.4 | A hello-world service deploys to staging on merge | S | Done | [#4](https://github.com/Mikay8/cascadia/pull/4) |
| 1.2 | Tenant provisioning: schema-per-tenant creation and the migration runner, using django-tenants if it checks out | 1.1 | Creating a tenant creates its schema and applies all migrations | M | Done | [#5](https://github.com/Mikay8/cascadia/pull/5) |
| 1.3 | Core tables and seed data | 1.2 | A seed script loads three fake tenants with funds, classes, investors, and loans | M | Done | [#6](https://github.com/Mikay8/cascadia/pull/6) |
| 1.4 | Authentication with MFA and short sessions | 1.1 | Login with MFA works on staging | M | In review | [#7](https://github.com/Mikay8/cascadia/pull/7) |
| 1.5 | Roles, permission checks, and the maker-checker mechanism | 1.3, 1.4 | The role matrix in `ROLES.md` is enforced by automated tests | M | Todo | |
| 1.6 | Audit log on every write | 1.3 | Every API write produces an audit row | S | Todo | |
| 1.7 | Tenant isolation test suite | 1.2, 1.5 | Every cross-tenant access attempt fails | S | Todo | |
| 1.8 | Design tokens and component library with Storybook | Design handoff | Each component matches the handoff and has empty and loading states | L | In progress | [#2](https://github.com/Mikay8/cascadia/pull/2) |
| 1.9 | Production database hardening on Railway: private networking, point-in-time recovery, high availability, restore drill | 1.2 | A restore drill is recorded with its recovery time | S | Todo | |
| 1.10 | AI guardrails: AI actor, audit fields, per-tenant switch, untrusted-input handling | 1.5, 1.6 | Tests show an AI actor cannot approve or execute, and every AI action is logged with its model and sources | M | Todo | |

Also in this phase: Railway project on the Pro plan with staging and production environments, Postgres on private networking only, confirm point-in-time recovery is available in the dashboard, download Railway's SOC 2 Type II report and bridge letter, ask Railway whether SSO, audit logs, and an uptime SLA need the Enterprise plan, and write the exit plan (AWS or Railway Enterprise) for the go-live review.

---

## Phase 2: Waterfall engines

**Goal:** a deterministic payout and loss engine proven against real past runs, with no UI needed.
**Depends on:** Phase 0 test material and decisions, Phase 1 schema.
**Gate:** reproduces the partner's Excel results to the cent.
**Rule:** tests come first on every increment here, and each one needs human review before merge.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Money and rounding library: decimal type and an allocation helper that always sums to the pool | Rounding decision | Property tests prove allocations sum exactly | S | Todo | |
| 2.2 | Ruleset model with validation and immutable versions | 1.3 | Invalid rulesets are rejected and saved versions cannot change | M | Todo | |
| 2.3 | Payout engine, simple case: return of principal for one class | 2.1, 2.2 | Matches golden case 1 | M | Todo | |
| 2.4 | Payout engine, full tiers: preferred return, catch-up, residual split, shortfalls | 2.3 | Matches every golden case | L | Todo | |
| 2.5 | Loss engine, including losses above total capital | 2.2 | Matches the loss golden cases | M | Todo | |
| 2.6 | Dry-run mode and input snapshots | 2.4, 2.5 | A run reproduces exactly from its snapshot | S | Todo | |
| 2.7 | Run lock, idempotency, atomic transaction, and reconciliation checks | 2.4 | Concurrent runs are rejected and any mismatch fails loudly | M | Todo | |
| 2.8 | Partner replay: run the partner's historical periods | 2.4 to 2.7 | Results match their Excel to the cent | S | Todo | |
| 2.9 | Structured calculation traces for every tier result | 2.4, 2.5 | Each allocated figure has a trace that recomputes to the same value | S | Todo | |

---

## Phase 3: Servicer ingestion

**Goal:** real loan activity flows in, is classified correctly, and feeds the engines.
**Depends on:** Phase 1 schema and queue, Phase 2 engines, a servicer sandbox from Phase 0.
**Gate:** a sandbox feed reaches the cash pool end to end.
**Note:** the first servicer's sandbox and sample payloads must be in hand before 3.3 starts.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 3.1 | Raw event intake: webhook endpoint, signature check, deduplication | 1.3 | A duplicate delivery is stored once | M | Todo | |
| 3.2 | Celery queue, workers, retries, and dead-letter queue | 3.1 | A failing event is retried, then dead-lettered | M | Todo | |
| 3.3 | Canonical event model and normalizer for the first servicer | 3.1, sandbox payloads | Every sample payload maps to the right canonical type | M | Todo | |
| 3.4 | Cash events: repayments, loan balances, and a cash pool with a settlement flag | 3.3 | The pool total equals the settled payments | M | Todo | |
| 3.5 | Advances and missed payments | 3.3 | Loan balances and delinquency status update correctly | S | Todo | |
| 3.6 | Defaults propose a loss allocation run | 3.3, 2.5 | A default creates a proposed loss allocation for approval | S | Todo | |
| 3.7 | Reversals and corrections | 3.4 | A bounced payment reverses the pool with no deleted history | M | Todo | |
| 3.8 | Unmatched events backend and nightly reconciliation against the servicer | 3.3 | Unmatched events are listed and balance differences are flagged | M | Todo | |
| 3.9 | Ingestion alerts | 3.2 | A failed or stalled feed alerts a person | S | Todo | |
| 3.10 | AI mapping suggestions for unrecognized event types | 3.3, 1.10 | Suggestions pass schema validation and cannot take effect without human approval | S | Todo | |
| 3.11 | AI loan-match suggestions for unmatched events | 3.8, 1.10 | Each suggestion carries a confidence score and needs a human to confirm it | S | Todo | |

---

## Phase 4: Admin product

**Goal:** a fund administrator can run the whole cycle through the UI, with every number traceable.
**Depends on:** Phase 1 components, Phase 2 engines, Phase 3 data.
**Gate:** the partner runs a shadow waterfall beside their Excel process.
**Note:** screens are built in this order so each is tested on real data produced by an earlier one.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 4.1 | App shell, navigation, tenant and fund switcher, and dashboard | 1.5, 1.8 | An admin logs in and sees the dashboard on seed data | M | Todo | |
| 4.2 | Servicing events feed and detail | 3.3, 4.1 | Raw payload and normalized event appear side by side | M | Todo | |
| 4.3 | Unmatched events queue and event correction flow | 3.8, 4.2 | An event can be matched, rejected, or corrected with a note, all audited | M | Todo | |
| 4.4 | Loan portfolio and loan detail | 3.4, 4.1 | Aging buckets and repayment history display correctly | M | Todo | |
| 4.5 | Capital stack and ruleset editor with approval | 2.2, 1.5 | A ruleset can be drafted, submitted, approved, and its history viewed | L | Todo | |
| 4.6 | Investors and capital account ledger | 1.3, 4.1 | A recorded contribution appears in the ledger | M | Todo | |
| 4.7 | Approvals inbox | 4.5, 1.5 | An approver cannot approve their own work | S | Todo | |
| 4.8 | Waterfall run flow: preview, simulate, execute, run detail | 2.6, 2.7, 4.7 | A run executes and every figure drills down to its source events | L | Todo | |
| 4.9 | Loss run detail | 2.5, 3.6 | A proposed loss run can be confirmed and its results viewed | M | Todo | |
| 4.10 | Shadow pilot with the partner | 4.1 to 4.9 | The log of mismatches against their Excel reaches zero | M | Todo | |
| 4.11 | AI ruleset drafting from an uploaded agreement, with clause citations | 4.5, 1.10, 0.5 | Drafted tiers cite their clauses and enter maker-checker like any other draft | M | Todo | |
| 4.12 | Run review agent that flags anomalies before approval | 4.8, 2.9, 1.10 | Flags appear on the approval screen and the agent cannot approve or execute | M | Todo | |
| 4.13 | Plain-language explanations in the Show calculation panel, plus AI match suggestions in the unmatched queue | 2.9, 4.3, 4.8, 3.11 | Explanations quote the stored trace and their numbers match it in tests | M | Todo | |

---

## Phase 5: Reports and go-live

**Goal:** investors and compliance needs are covered and the platform is safe for a real tenant.
**Depends on:** Phase 4 and a clean shadow pilot.
**Gate:** one real period run live with the partner.
**Note:** reporting and portal increments can run in parallel once Phase 4 is stable; 5.9 and 5.10 come last and need human work beyond Claude Code.

| ID | Increment | Depends on | Done when | Size | Status | PR |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1 | Investor statements as PDF | 4.6, 4.8 | Statement totals reconcile to the ledger | M | Todo | |
| 5.2 | Fund reports and CSV exports | 4.4, 4.8 | Exports open in Excel and match the screens | M | Todo | |
| 5.3 | Impact metrics model and screens | Partner's data source | Impact metrics show beside financial figures | M | Todo | |
| 5.4 | Investor portal | 1.5, 5.1 | Isolation tests prove an investor sees only their own data | L | Todo | |
| 5.5 | Auditor view with time-limited access | 1.5 | Auditor access expires automatically | M | Todo | |
| 5.6 | Settings: users, roles, funds, and servicer connections | 1.5 | A tenant admin manages these without an engineer | M | Todo | |
| 5.7 | Audit log viewer | 1.6 | An entry can be searched and opened to show before and after | M | Todo | |
| 5.8 | Platform console and support-access requests | 1.5 | Support access needs tenant approval and is logged | M | Todo | |
| 5.9 | Hardening: penetration test fixes, load test, backup drill, alerting | 5.1 to 5.8 | All penetration test findings are closed | M | Todo | |
| 5.10 | Launch readiness: runbook, help content, contract review, SOC 2 evidence | 5.9 | The partner runs one real period live | M | Todo | |
| 5.11 | AI report drafting: investor letters, board summaries, impact narratives, CDFI Fund report text | 5.1, 5.2, 5.3, 1.10 | Drafts cite the figures they use and a human edits before anything is sent | M | Todo | |
| 5.12 | Investor-facing balance explanations in the portal | 5.4, 2.9 | Explanations show only the investor's own amounts, proven by isolation tests | S | Todo | |
| 5.13 | AI evaluation suite and release checks | 0.2, 0.5, 4.11, 4.13 | Accuracy on the golden cases is measured and tracked for every release | M | Todo | |

Later, after launch: ask-your-data questions scoped by role, and a read-only API for customers' own AI tools.
