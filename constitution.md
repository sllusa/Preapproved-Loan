# Préstamo Preconcedido (Ruralvía) — Implementation Constitution

<!-- Derived from the RSI / Ruralvía functional specification. Governs the build, not the org. -->

## Core Principles

### I. No Signature Without Precontractual Disclosure
The system MUST present the standardized precontractual information (INE/SECCI) and the
contract to the customer, and MUST record the customer's acceptance with an evidence
timestamp, BEFORE any signature can begin. The system MUST NOT allow the signature step to
start while acceptance of the precontractual documentation is unrecorded.
**Rationale:** Ley 16/2011 (consumer credit) makes standardized precontractual disclosure a
legal precondition of contracting; skipping it voids the transparency guarantee and exposes
the entity to regulatory sanction. The successor CCD2 (Directive (UE) 2023/2225, applying from
20-Nov-2026) preserves and reinforces this precondition — the control MUST survive that transition.

### II. Strong Customer Authentication Is Mandatory
The system MUST complete a successful PSD2 Strong Customer Authentication (SCA) before a loan
can move to the signed state. If SCA fails or is cancelled, the system MUST NOT sign, disburse,
or create the loan; it may only offer a bounded number of retries and then pause the flow.
**Rationale:** PSD2 / RD-ley 19/2018 requires SCA for digital contracting; disbursing without
it is an unauthenticated commitment of funds.

### III. Disbursement Is Idempotent and Gated
The system MUST execute the disbursement only after a successful signature and successful
verifications. A disbursement MUST NOT be duplicated under retries or timeouts: a repeated
disbursement request for the same loan MUST be recognized and produce no second credit.
**Rationale:** DORA operational-resilience requirements and basic financial correctness make a
double credit an unacceptable, potentially unrecoverable error.

### IV. Verifications Gate Digital Closure
The system MUST run a light solvency evaluation and antifraud/AML (PBC/FT) verification before
signature. If the verifications are not passed, the system MUST NOT complete the contract
digitally; it MUST route the case to a human channel (advisor/branch) and stop the digital flow.
**Rationale:** Ley 16/2011 art. 14 (solvency) and Ley 10/2010 (PBC/FT) require proportionate
checks; auto-closing an un-verified case is a compliance breach.

### V. Only Live Offers May Originate a Loan
The system MUST NOT originate a loan from an offer that is expired (`CADUCADA`) or revoked
(`REVOCADA`). If the offer expires or is revoked at any point before the signed state, the
system MUST stop the flow and inform the customer clearly.
**Rationale:** An expired or revoked offer no longer reflects an approved risk decision;
honoring it would extend credit outside the sanctioned risk envelope.

### VI. Simulation Must Stay Within the Offer
Every simulation the system produces MUST respect `importe ≤ importeMax` and
`plazo ≤ plazoMax` of the customer's live offer. The system MUST NOT let the customer
configure or advance a loan whose amount or term exceeds the offer's limits.
**Rationale:** The offer's amount and term are the boundaries of the pre-approved credit
decision; exceeding them turns a pre-approved product into an un-underwritten one.

### VII. Build Once, Parameterize Per Entity
The journey MUST be a single, common implementation (one flow, one rule set, one IRIS
integration) whose per-entity differences — brand, product catalog (amount/term limits, TIN,
fees, relationship bonus), legal-text templates, and locale — are resolved **only** through a
per-entity configuration layer, never through forked code. The system MUST NOT expose or
originate a loan for an entity without a valid, resolved configuration. The common regulatory
baseline (Ley 16/2011, PSD2, RGPD, DORA) is invariant and MUST NOT be weakened by any per-entity
parameter.
**Rationale:** Ruralvía is a multi-entity platform serving ~30 autonomous credit unions of Grupo
Caja Rural over a common channel and a common core (IRIS); fragmenting into per-entity codebases
would multiply core-regression risk and defeat the "build once, deploy to many" mandate that
justifies the pilot.

## Compliance & Hard Constraints

- **Precontractual rights disclosure:** The system MUST inform the customer of the right of
  withdrawal (14 calendar days, Ley 16/2011 art. 28) and of early repayment (art. 30) before
  signature.
- **Accessibility:** The customer-facing journey MUST meet WCAG 2.1 AA (contrast, focus order,
  screen-reader operability, keyboard-only completion).
- **Data protection & automated decisions:** Personal-data processing and the scoring/automated
  decision MUST comply with RGPD/LOPDGDD, including informing the customer and honoring data
  subject rights; sensitive data MUST NOT appear in logs.
- **Immutable audit:** Every acceptance, signature, and disbursement MUST be recorded to an
  immutable audit trail (who, what, when).
- **Eligible disbursement account:** The disbursement account MUST be an account the customer
  holds at the entity, active and operable.
- **Legal baseline & transition:** The consumer-credit baseline is Ley 16/2011 (transposing
  Directive 2008/48/CE), transitioning to **CCD2 (Directive (UE) 2023/2225, application 20-Nov-2026)**.
  Precontractual disclosure (SECCI/INE), the solvency evaluation, the 14-day right of withdrawal,
  early repayment, and TAE MUST hold under both frames. The exact Spanish transposition date is to
  be confirmed with RSI.

## Reliability Posture

Statistical performance and conversion targets (response-time, conversion uplift, CSAT/NPS) are
deferred to a later iteration that includes an eval/measurement harness. MVP acceptance is
functional — see quickstart.md.

## Governance

This constitution supersedes ad-hoc implementation choices. The `plan.md` Constitution Check
gate MUST pass before implementation begins. Amendments require re-running the spec generator
against an updated functional specification.

**Version**: 1.1.0 | **Ratified**: 2026-07-06 | **Last amended**: 2026-08-03 | **Source**: RSI / Ruralvía functional specification

<!-- v1.1.0 — Added Principle VII (build once, parameterize per entity); added CCD2 (Directive
(UE) 2023/2225) transition to Principle I and the legal-baseline constraint. This file is the
single canonical constitution; the earlier constitution-v2.md draft has been folded in and removed. -->

