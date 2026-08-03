# Quickstart: Pre-Approved Loan Journey

## Acceptance gate (Definition of Done)
MVP acceptance is functional and verified by running the system:
- The journey processes the happy-path fixture customer end to end — discovery → offer detail →
  simulation → summary/account → precontractual → verification → SCA → disbursement →
  confirmation — with no manual step.
- Every state transition in the data-model.md loan lifecycle fires on at least one fixture case
  (including the verification-fail path to `RECHAZADA_VERIFICACION`).
- Every business rule (BR-01–BR-14) and field validation (FV-01–FV-05) executes on the fixture
  cases.
- Every screen in the interfaces.md UI Contracts section renders with seed data, and the journey
  is completable using keyboard and screen reader only.
- A repeated disbursement request for the same fixture loan produces no second credit.
- The same journey runs for fixture customers of two distinct entities and each renders its own
  brand, product limits/rates, and legal texts from EntityConfiguration alone, with no per-entity
  code path (SC-006 / BR-15/BR-16).

No percentage accuracy or latency targets at MVP.

## How to verify (manual)
1. Seed the fixtures across at least two entity configurations (brand, catalog, legal templates,
   locale): a live-offer customer (Marta), a verification-fail customer routed to human (Andrés), a
   senior accessibility/resume case (Rosa), a no-operable-account case, and an expired-offer case —
   with Marta and at least one other customer belonging to different entities.
2. Run the journey for Marta and observe it reach `ABONADO`/`ACTIVO` with an amortization schedule
   and a confirmation showing the loan number.
3. Run the journey for Andrés and observe the verification gate stop the digital flow and offer a
   human channel (`RECHAZADA_VERIFICACION`).
4. Attempt to sign before accepting the precontractual document and observe the block (BR-06/FV-04).
5. Attempt an amount above the offer maximum and observe the clamp and notice (BR-02/FV-01).
6. Re-issue the disbursement request for Marta's loan and observe no second credit.
7. Complete Marta's journey with keyboard and screen reader only.
8. Run the journey for customers of two different entities and confirm each shows its own brand,
   product limits/rates, and legal texts from configuration alone — same code path (SC-006).
