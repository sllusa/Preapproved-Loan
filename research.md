# Phase 0 Research: Pre-Approved Loan Journey

## Clarifications resolved

### #1 — Behaviour when the offer expires or is revoked mid-flow
- **Decision**: Stop the flow at the current step and mark the offer terminal (`CADUCADA`/
  `REVOCADA`); show a clear message with a contact route. No grace period is granted for MVP.
- **Rationale**: An expired/revoked offer no longer represents an approved risk decision
  (Constitution V); stopping is the safe default and matches alternative flow A2 in the source.
  Recorded under spec.md Assumptions and flagged for RSI confirmation.
- **Alternatives considered**: A short grace window to let a nearly-complete signature finish —
  rejected for MVP because it complicates the risk envelope and needs a policy from RSI.

### #2 — Handling a customer with multiple live offers
- **Decision**: Use the single most recent live offer; do not present an offer picker in MVP.
- **Rationale**: The source lists multi-offer prioritization as an open question to define with
  RSI; a deterministic "most recent live offer" default keeps the happy path unambiguous while a
  real prioritization policy is pending. Recorded under spec.md Assumptions.
- **Alternatives considered**: An offer-selection screen — deferred until RSI defines the
  prioritization rule, to avoid inventing product policy.

### #3 — Multi-entity parametrization ("build once, deploy to many")
- **Decision**: Ship a single common journey whose per-entity differences (brand, product catalog,
  legal-text templates, locale) are resolved through an EntityConfiguration layer (MCP-T09); the
  MVP seeds ≥2 entities to prove parametrization. No per-entity code path.
- **Rationale**: Ruralvía serves ~30 autonomous credit unions of Grupo Caja Rural over a common
  channel and the common IRIS core; forking per entity multiplies core-regression risk and defeats
  the pilot's mandate (Contexto_Idiosincrasia BR-ORG-01..09; Constitution Principle VII).
- **Alternatives considered**: Per-entity forks or a single hard-coded entity — rejected as
  contradicting the platform reality and the replicability goal.

### #4 — Legal baseline and CCD2 transition
- **Decision**: Build to Ley 16/2011 while keeping the controls (SECCI/INE, solvency, 14-day
  withdrawal, early repayment, TAE) valid under CCD2 (Directive (UE) 2023/2225, application
  20-Nov-2026). Exact Spanish transposition date to confirm with RSI.
- **Rationale**: CCD2 preserves and reinforces these obligations; designing to survive the
  transition avoids rework (Marco_Legal_Lending_UE_Espana §1.1).
- **Alternatives considered**: Ignoring CCD2 for MVP — rejected because application lands within
  the pilot horizon.

## Tech-stack resolution
- **Platform = ICA (Context Studio + SDLC Agentic App)** — Decision: build within the named
  platform context. Source: Project context (the functional spec names it as the pilot platform).
- **Front-end = React, no design-system library** — Decision: plain React for MVP. Source:
  Decided by user; the group design system is referenced but unnamed in the source and is deferred.
- **Back-end = Python 3.11 + Anthropic SDK direct** — Decision: pro-code agents via the Anthropic
  SDK. Source: Decided by user.
- **Storage = local filesystem** — Decision: fixtures and journey state on the filesystem for MVP.
  Source: Decided by user.
- **Observability = structured logging (Control Tower deferred)** — Decision: stdout logging for
  MVP. Source: Project context + Default for MVP.

## Scope-boundary decisions
- **Orphaned upstream dependency (Pattern 2):** every in-scope agent's inputs are produced either
  by an upstream in-scope agent or by a mocked external system, so no orphan exists — seed
  fixtures supply entity configuration, offers, accounts, pricing, documents, verification, and SCA
  outcomes (data-model.md).
- **Mid-stream scope cut (Pattern 1):** the disbursement output (loan + schedule) is consumed by
  the confirmation screen (in scope); post-contracting management (US3) is the deferred consumer,
  terminating the MVP at `ACTIVO`.
- **UX/scope mismatch (Pattern 3):** every UI screen's data is produced by an in-scope agent or
  mocked tool; no screen was dropped.
