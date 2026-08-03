# Feature Specification: Pre-Approved Loan Journey — RSI / Ruralvía (Grupo Caja Rural)

**Feature Branch**: `001-prestamo-preconcedido`
**Created**: 2026-07-06
**Status**: Draft
**Input**: RSI / Ruralvía functional specification for the pre-approved consumer loan journey

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contract a pre-approved loan end to end (Priority: P1) 🎯 MVP

An eligible customer with a live pre-approved offer discovers the offer inside Ruralvía,
adjusts the amount and term while seeing the monthly payment and total cost update in real
time, chooses the account to receive the money, reviews and accepts the standardized
precontractual information, passes the verifications, signs with strong authentication, and
receives the funds in their account with an amortization schedule and a confirmation — all
digitally, without visiting a branch.

**Why this priority**: This is the whole point of the pilot — a fully digital, transparent,
minutes-long contracting journey for a pre-approved offer. Everything else is a refinement of
or a follow-on to this one thread.

**Independent Test**: Run the journey on a single fixture customer with a live offer and
confirm it reaches the disbursed state with an amortization schedule generated and a
confirmation shown, with every business rule exercised along the way.

**Acceptance Scenarios**:
1. **Given** a customer with a live offer of a set maximum amount and term, **When** they set
   the amount and term within the offer, **Then** the monthly payment, nominal rate, effective
   rate, and total cost are shown and update on each change.
2. **Given** a customer who tries to set an amount above the offer maximum, **When** they
   confirm, **Then** the system limits the amount to the offer maximum and shows a notice.
3. **Given** a customer who has not accepted the precontractual documentation, **When** they
   attempt to sign, **Then** the system blocks signature and returns them to the precontractual
   information.
4. **Given** successful strong authentication and passed verifications, **When** the signature
   completes, **Then** the loan is created, the amount is credited to the chosen account, an
   amortization schedule is generated, and the credit is not duplicated on retry.

### User Story 2 - Handle a customer who cannot close digitally (Priority: P2)

A customer configures a loan but the verifications (solvency / antifraud / AML) are not
passed. Instead of a hard failure, the customer is told the contract cannot be completed
online and is offered a route to a human advisor or branch, while the digital flow stops.

**Why this priority**: Necessary for a real pilot but not required to prove the happy path;
the MVP can demonstrate the gate exists (US1 scenario) while the full advisor hand-off is a
follow-on increment.

**Independent Test**: Run the journey on a fixture customer whose verification fails and
confirm the digital flow stops and an advisor-routing outcome is recorded.

**Acceptance Scenarios**:
1. **Given** a customer whose verification is not passed, **When** verifications complete,
   **Then** the digital flow stops and the customer is offered a human channel.

### User Story 3 - Manage a live loan after disbursement (Priority: P3)

After disbursement, the customer can view the loan from their global position, consult the
amortization schedule and documentation, and reach the entry points for early repayment and
for exercising the 14-day right of withdrawal.

**Why this priority**: Valuable post-contracting management, but outside the minimal thread
that proves digital origination; deferred to a later iteration.

**Independent Test**: From a disbursed fixture loan, confirm the loan, schedule, and
documentation are viewable and the withdrawal/early-repayment entry points are present.

**Acceptance Scenarios**:
1. **Given** a disbursed loan, **When** the customer opens it, **Then** the schedule and
   documentation are shown with entry points to early repayment and withdrawal.

### Edge Cases

- The offer expires or is revoked while the customer is still configuring — the flow must stop
  with a clear message [NEEDS CLARIFICATION: exact revocation-during-flow behaviour and grace
  handling — see research.md].
- The customer has no active, operable account to receive funds — the flow must block and guide
  them to choose another account.
- A core timeout occurs during disbursement — the loan must sit in a pending state and reconcile
  without ever crediting twice.
- The customer starts on the app and resumes on the web (or vice versa) — the configured state
  must be shared.
- The customer has more than one live offer [NEEDS CLARIFICATION: how to prioritize or let the
  customer select among multiple live offers — see research.md].
- The journey must be completable using only a screen reader and keyboard.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present the pre-approved offer to eligible customers and MUST NOT
  expose the journey when there is no live offer.
- **FR-002**: System MUST show the offer detail: maximum amount, indicative term, nominal rate,
  and validity.
- **FR-003**: System MUST let the customer configure the amount and term, bounded by the
  offer's maximum amount and maximum term.
- **FR-004**: System MUST recalculate and display the monthly payment, nominal rate, effective
  rate, and total cost on every change of amount or term.
- **FR-005**: System MUST show the rate with and without relationship bonus when a bonus applies.
- **FR-006**: System MUST let the customer save a simulation and resume it while the offer
  remains live.
- **FR-007**: Users MUST be able to select the disbursement account from their own active,
  operable accounts.
- **FR-008**: System MUST present the standardized precontractual information (INE/SECCI) and
  the contract, allow the customer to read and download them, and record acceptance with a
  timestamp before signature.
- **FR-009**: System MUST inform the customer of the 14-day right of withdrawal and of early
  repayment.
- **FR-010**: System MUST run a light solvency evaluation and an antifraud/AML verification
  before signature and MUST NOT allow digital closure when they are not passed; it MUST offer a
  human channel instead — enforced by the verification rule set (see the Business Rules section).
- **FR-011**: System MUST complete a successful strong customer authentication before signature
  and MUST NOT sign, create, or disburse the loan if authentication fails or is cancelled.
- **FR-012**: System MUST create the loan and credit the chosen account only after successful
  signature and verifications, and MUST NOT duplicate the credit under retries or timeouts.
- **FR-013**: System MUST generate and display the amortization schedule once the loan is
  disbursed.
- **FR-014**: System MUST show a confirmation with the loan number, a summary, and access to
  the documentation, and MUST record every acceptance, signature, and disbursement to an
  immutable audit trail.
- **FR-015**: System MUST stop the flow with a clear message if the offer expires or is revoked
  before signature, and MUST NOT originate a loan from an expired or revoked offer.

### Key Entities *(include if feature involves data)*

- **Customer**: an eligible individual using Ruralvía, holding a live pre-approved offer and one
  or more accounts.
- **PreApprovedOffer**: a live, pre-approved financing offer for a customer, with a maximum
  amount, maximum term, nominal rate, and validity.
- **Simulation**: a configured amount/term with its computed payment and cost figures, derived
  from an offer.
- **Loan**: the contracted loan originated from a simulation, with a lifecycle and a disbursement.
- **AmortizationSchedule**: the ordered set of installments for a loan.
- **PrecontractualDocument**: the INE/SECCI and contract shown and accepted before signature.
- **DisbursementAccount**: the customer's account that receives the funds.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The journey processes a fixture customer with a live offer end to end — from
  discovery to disbursement — with no manual step.
- **SC-002**: Every state transition in the loan lifecycle fires on at least one fixture case.
- **SC-003**: Every business rule and field validation executes on the fixture cases, including
  the amount/term limit, precontractual-before-signature, verification gate, and SCA gate.
- **SC-004**: Every screen renders with seed data, and the journey is completable with keyboard
  and screen reader only.
- **SC-005**: A repeated disbursement request for the same fixture loan produces no second
  credit.

## Assumptions

- MVP tier, Single UC Happy Path: the P1 end-to-end thread is delivered; the failed-verification
  hand-off (US2) is demonstrated as a stopping gate but the full advisor routing is deferred.
- Post-contracting management (US3: amortization query, withdrawal, early repayment) is out of
  scope for this iteration.
- All external systems — offer/scoring engine, pricing engine, core banking, signature/SCA,
  antifraud/AML, document manager, notifications, and the risk register (CIRBE) — are mocked
  from fixtures for this iteration.
- Payment protection insurance cross-sell is out of scope.
- Where the offer expires during the flow, the default is to stop at the current step and mark
  the offer terminal; where a customer has multiple live offers, the default is to use the
  single most recent live offer. Both defaults are flagged for confirmation (see research.md).
- Product parameters (amounts, terms, rates, fees, bonus) are reference values to be confirmed
  with RSI.
