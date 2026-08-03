# Tasks: Pre-Approved Loan Journey

**Input**: spec.md, plan.md, data-model.md, contracts/interfaces.md
**Prerequisites**: plan.md complete; contracts/ generated
**Organization**: grouped by user story (US1, US2, US3) for independent delivery

## Component Conventions
Tasks reference work by ID — `AGT-XX`, `MCP-TXX`, `BR-NN`/`FV-NN`, entities/enums by name, `US#`
— **never file paths**. The coding agent decides layout.

## Phase 1: Setup
- T001 [P] Establish the project skeleton and dependency baseline (Python 3.11 + Anthropic SDK; React front end) per plan.md Technical Context
- T002 [P] Establish structured stdout logging and the audit-event recording convention (BR-14)

## Phase 2: Foundational (blocking)
- T003 Define the data-model.md entities (EntityConfigurationRecord, CustomerRecord, PreApprovedOfferRecord, SimulationRecord, LoanRecord, AmortizationSchedule, Installment, PrecontractualDocument, VerificationResult, SignatureResult, DisbursementAccountRecord) and the shared enums (OfferStatus, LoanStatus) as common types
- T004 Implement the AGT-07 Journey Orchestrator shell and the loan-lifecycle state machine per data-model.md, enforcing step ordering and carrying the resolved entity_config through the journey
- T005 [P] Build the mocked external tools MCP-T01–MCP-T09 returning the fixture shapes in data-model.md
- T006 [P] Author the seed fixtures (happy-path, verification-fail, senior/resume, no-operable-account, expired-offer) across at least two entity configurations
- T006b [P] Author the per-entity EntityConfiguration fixtures (≥2 entities: brand, product catalog, legal-text templates, locale, feature flags) served by MCP-T09
**Checkpoint:** shared model, orchestrator shell, entity configs, and mocked tools in place; story work can begin.

## Phase 3: User Story 1 — Contract a pre-approved loan end to end (P1) 🎯 MVP
**Goal:** deliver the full digital origination thread from discovery to disbursement.
**Independent Test:** run the happy-path fixture customer and confirm the loan reaches disbursed/active with a schedule and confirmation, every rule exercised.
- T007 [US1] Implement AGT-01 (Offer Discovery) per its interfaces.md I/O; resolve entity_config via MCP-T09 and enforce BR-01/BR-12/BR-15 via MCP-T01
- T008 [US1] Implement AGT-02 (Simulation & Pricing) per its I/O; apply entity_config catalog/bonus and enforce BR-02–BR-05 and FV-01/FV-02 via MCP-T02 (depends on T007)
- T009 [US1] Implement account selection using MCP-T07; enforce BR-10 and FV-03
- T010 [US1] Implement AGT-03 (Precontractual) per its I/O; enforce BR-06, BR-11, FV-04 via MCP-T03 (depends on T008)
- T011 [US1] Implement AGT-04 (Verification) per its I/O; enforce BR-09 via MCP-T04 (depends on T010)
- T012 [US1] Implement AGT-05 (Signature/SCA) per its I/O; enforce BR-07 and FV-05 via MCP-T05 (depends on T011)
- T013 [US1] Implement AGT-06 (Disbursement) per its I/O; enforce BR-08 idempotency and generate the AmortizationSchedule via MCP-T06/MCP-T07/MCP-T08 (depends on T012)
- T014 [P] [US1] Build the UI Contracts screens (offer discovery, offer detail, simulation, summary & account, precontractual, verification status, signature, confirmation) consuming the agent outputs, themed/localized from entity_config (BR-15), keyboard/screen-reader operable
- T014b [US1] Verify parametrization (SC-006): run US1 for fixture customers of two entities and confirm each renders its own brand, product limits/rates, and legal texts from configuration alone, with no per-entity code path
**Checkpoint:** US1 is independently functional and testable end to end.

## Phase 4: User Story 2 — Handle a customer who cannot close digitally (P2)
**Goal:** stop the digital flow and route to a human when verification fails.
**Independent Test:** run the verification-fail fixture and confirm the flow stops at RECHAZADA_VERIFICACION with a human-channel outcome.
- T015 [US2] Extend AGT-04 and AGT-07 to set `route_to_human` and stop digital closure (BR-09), recording the routing to the audit trail
- T016 [US2] Build the human hand-off state on the verification screen per the UI Contracts reviewer surface
**Checkpoint:** US1 and US2 both work independently.

## Phase 5: User Story 3 — Manage a live loan after disbursement (P3)
**Goal:** post-contracting view of the loan, schedule, documentation, and rights entry points.
**Independent Test:** from a disbursed fixture loan, confirm the loan, schedule, and documentation are viewable with withdrawal/early-repayment entry points.
- T017 [US3] Implement the post-contracting view consuming AGT-06 outputs (loan, schedule) and the precontractual documentation, with entry points for early repayment and 14-day withdrawal
**Checkpoint:** US1–US3 each independently testable.

## Phase N: Polish & Cross-Cutting
- T018 [P] Harden the edge cases from spec.md (offer expiry/revocation mid-flow, no operable account, core timeout to PENDIENTE_ABONO with reconciliation, cross-channel resume)
- T019 [P] Verify keyboard/screen-reader completion of the full journey (WCAG 2.1 AA operability)

## Dependencies & Execution Order
- Setup (Phase 1) → Foundational (Phase 2, blocks all stories) → US1 (P1) → US2 (P2) → US3 (P3) → Polish.
- Within US1: T007 → T008 → T010 → T011 → T012 → T013 in sequence; T009 and T014 alongside once their inputs exist.

## Parallel Example
T001, T002 together; T005, T006, T006b together; T014 alongside the US1 agent tasks; T018, T019 together.

## Implementation Strategy
MVP-first: complete Setup + Foundational + US1, validate against quickstart.md, then add US2 and
US3 as independent increments.
