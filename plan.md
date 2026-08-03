# Implementation Plan: Pre-Approved Loan Journey

**Branch**: `001-prestamo-preconcedido` | **Date**: 2026-07-06 | **Spec**: ./spec.md

## Summary
Deliver a fully digital, mobile-first web journey that lets an eligible Ruralvía customer
discover a live pre-approved offer, simulate amount and term with transparent figures, accept
the precontractual documentation, pass verifications, sign with SCA, and receive an idempotent
disbursement with an amortization schedule. The MVP builds the P1 end-to-end thread as a set of
synthesized agents orchestrated over the loan lifecycle, with every external system mocked. The
journey is a single common implementation parameterized per entity ("build once, deploy to many"):
brand, product catalog, legal-text templates, and locale enter through EntityConfiguration, and
the MVP seeds at least two entities to prove parametrization without forking the flow.

## Technical Context
**Language/Version**: Python 3.11 — Source: Decided by user
**Primary Dependencies**: Anthropic SDK direct for agent logic — Source: Decided by user; agent/tool decomposition synthesized from the journey — Source: Blueprint (functional spec)
**Storage**: Local filesystem (JSON/CSV fixtures + journey state) for MVP — Source: Decided by user
**Models per agent**: Not specified in the source; a single general reasoning model for the reasoning agent (AGT-04), deterministic logic elsewhere — Source: Default for MVP
**Orchestration**: Supervisor/orchestrator agent (AGT-07) sequencing step agents over the loan lifecycle — Source: Blueprint (journey state model)
**Front-end**: React (no design system library — the group design system is deferred) — Source: Decided by user
**Observability**: Structured logging to stdout for MVP; Control Tower wiring deferred — Source: Project context (ICA / Context Studio) + Default for MVP
**Testing**: pytest — Source: Default for MVP
**Target Platform**: ICA (Context Studio + SDLC Agentic App) — Source: Project context (functional spec names the platform)
**Project Type**: web
**Scope tier**: MVP — Single UC Happy Path: the P1 digital origination thread, all externals mocked.
**Performance/Reliability Goals**: Functional acceptance only; statistical targets (recálculo < 300 ms, conversion uplift, CSAT/NPS, WCAG audit scoring) deferred to a later iteration with a measurement/eval harness in scope.

## Constitution Check
*GATE: must pass before Phase 0. Re-check after Phase 1.*

| Principle | Compliance in this plan |
|-----------|-------------------------|
| I. No Signature Without Precontractual Disclosure | AGT-03 records acceptance before AGT-05 can run; enforced by BR-06/FV-04 and the orchestrator ordering. |
| II. Strong Customer Authentication Is Mandatory | AGT-05 gates FIRMADO on `signature.succeeded`; failure blocks disbursement (BR-07). |
| III. Disbursement Is Idempotent and Gated | AGT-06 / MCP-T06 use `idempotency_key`; the mock core returns the same result on repeat (BR-08). |
| IV. Verifications Gate Digital Closure | AGT-04 must pass before AGT-05; failure sets `route_to_human` and stops digital closure (BR-09). |
| V. Only Live Offers May Originate a Loan | AGT-01 exposes the journey only for OFERTA_VIGENTE; orchestrator stops on expiry/revocation (BR-01/BR-12). |
| VI. Simulation Must Stay Within the Offer | AGT-02 clamps amount/term to the offer (BR-02/BR-03, FV-01/FV-02). |
| VII. Build Once, Parameterize Per Entity | AGT-01 resolves `entity_config` via MCP-T09 and gates exposure on it (BR-15); a single flow drives all entities, params only (BR-16); AGT-07 stamps the entity on audited events. |
| Compliance — rights disclosure | Shown by AGT-03 before signature (BR-11). |
| Compliance — accessibility (WCAG 2.1 AA) | React screens built to keyboard/screen-reader operability; formal audit deferred. |
| Compliance — data protection / scoring | Verification inputs minimized; no sensitive data in logs. |
| Compliance — immutable audit | AGT-06 writes acceptance/signature/disbursement events (BR-14). |
| Compliance — operable disbursement account | Enforced by FV-03 / BR-10 via MCP-T07. |

No violations — Complexity Tracking omitted.

## Project Structure

### Documentation (this feature)
```text
specs/001-prestamo-preconcedido/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md
└── contracts/interfaces.md
```

### Source Code
**Structure Decision**: web (a React front end plus a Python agent/orchestration back end). The
coding agent designs the concrete module and directory layout; this plan names only the project
type.

## Integration Strategy
All external systems are MOCK for this iteration:
- **Offer/scoring engine (MCP-T01):** seed offer fixtures keyed by customer.
- **Pricing engine (MCP-T02):** deterministic fixture pricing function.
- **Document manager (MCP-T03):** fixture INE/SECCI PDF references with acceptance stamping.
- **Verification & risk register / CIRBE + antifraud (MCP-T04):** scripted pass/fail per fixture customer, so the verification gate and the human hand-off can both be exercised.
- **Signature / SCA (MCP-T05):** scripted success/failure to exercise the SCA gate and retries.
- **Core banking / disbursement (MCP-T06) — the only "hard" integration in production:** in-memory stub recording credits by `idempotency_key` and returning the same result on repeat, so double-credit is provably impossible; the real RSI core is the single deferred hard integration.
- **Account lookup (MCP-T07):** fixture account rows, including a non-operable-account case.
- **Notifications (MCP-T08):** no-op sink recording the confirmation payload.
- **Entity configuration (MCP-T09):** seed configs for at least two entities (brand, catalog, legal templates, locale), so the same flow renders each entity's brand/limits/rates/texts from parameters alone.

Fixture *shapes* live in data-model.md. Variety to cover: a happy-path customer (Marta), a
verification-fail customer routed to human (Andrés), a senior accessibility/resume case (Rosa), a
no-operable-account case, an expired-offer case, and customers spread across two entities so the
parametrization (SC-006) is exercised.

<!-- No production auth/secrets, memory tier, or eval harness in this MVP; they are deferred. -->
