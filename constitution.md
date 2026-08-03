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
the entity to regulatory sanction.

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

## Reliability Posture

Statistical performance and conversion targets (e.g. recálculo < 300 ms, conversion uplift,
CSAT/NPS) are deferred to a later iteration that includes an eval/measurement harness. MVP
acceptance is functional — see quickstart.md.

## Governance

This constitution supersedes ad-hoc implementation choices. The `plan.md` Constitution Check
gate MUST pass before implementation begins. Amendments require re-running the spec generator
against an updated functional specification.

**Version**: 1.0.0 | **Ratified**: 2026-07-06 | **Source**: RSI / Ruralvía functional specification
