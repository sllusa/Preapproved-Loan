# Agent Contracts: Pre-Approved Loan Journey

<!-- No formal agent register existed in the source functional specification; the agents below
     are synthesized from the journey steps. All I/O fields are marked [synthesized]. -->

| Agent ID | Name | Atomic Steps | Type | Zone | Status |
|----------|------|--------------|------|------|--------|
| AGT-01 | Offer Discovery Agent | S01, S02 | Deterministic | Green | BUILD |
| AGT-02 | Simulation & Pricing Agent | S03, S04 | Deterministic | Green | BUILD |
| AGT-03 | Precontractual Agent | S05 | Deterministic | Amber | BUILD |
| AGT-04 | Verification Agent | S06 | Reasoning | Amber | BUILD |
| AGT-05 | Signature (SCA) Agent | S07 | Action | Amber | BUILD |
| AGT-06 | Disbursement Agent | S08, S09 | Action | Red | BUILD |
| AGT-07 | Journey Orchestrator | S01–S09 | Deterministic | Amber | BUILD |
| AGT-08 | Post-Contracting Agent | S10 | Deterministic | Green | OUT OF SCOPE |

## Agent specifications

### AGT-01 — Offer Discovery Agent (BUILD)
Retrieves the customer's live pre-approved offer from the mocked offer/scoring engine and
determines whether the journey should be exposed at all. It surfaces the offer detail — maximum
amount, indicative term, nominal rate, and validity — and refuses to expose the journey when no
live offer exists. It is the gatekeeper that enforces "only live offers may originate a loan."

**Inputs:**
- `customer_id` (str) [synthesized] — the customer requesting the journey

**Outputs:**
- `offer` (PreApprovedOfferRecord) [synthesized] — the live offer, if any
- `journey_available` (bool) [synthesized] — whether the journey may be shown

### AGT-02 — Simulation & Pricing Agent (BUILD)
Takes the customer's requested amount and term, clamps them to the offer's limits, and calls the
mocked pricing engine to compute the monthly payment, nominal rate, effective rate, and total
cost. It recomputes on every change and returns the rate with and without relationship bonus when
applicable, so the simulation screen can display transparent figures in real time.

**Inputs:**
- `offer` (PreApprovedOfferRecord) [synthesized] — the live offer providing limits
- `requested_amount` (decimal) [synthesized] — customer's requested amount
- `requested_term_months` (int) [synthesized] — customer's requested term

**Outputs:**
- `simulation` (SimulationRecord) [synthesized] — computed payment and cost figures
- `amount_clamped` (bool) [synthesized] — whether the amount was limited to the offer maximum

### AGT-03 — Precontractual Agent (BUILD)
Produces the standardized precontractual documentation (INE/SECCI) and contract via the mocked
document manager, presents them for reading and download, and records the customer's acceptance
with an evidence timestamp. It is the control that guarantees no signature can begin before the
precontractual documentation has been shown and accepted, and it surfaces the withdrawal and
early-repayment rights.

**Inputs:**
- `simulation` (SimulationRecord) [synthesized] — the confirmed simulation
- `disbursement_account` (str) [synthesized] — the chosen account

**Outputs:**
- `document` (PrecontractualDocument) [synthesized] — the presented document with acceptance state
- `accepted` (bool) [synthesized] — whether acceptance was recorded

### AGT-04 — Verification Agent (BUILD)
Runs the light solvency evaluation and the antifraud/AML (PBC/FT) verification against the mocked
verification and risk-register services before signature. It returns a consolidated pass/fail; on
failure it signals that the digital flow must stop and route to a human channel. It enforces the
verification gate that must clear before signature.

**Inputs:**
- `customer_id` (str) [synthesized] — the customer under verification
- `simulation` (SimulationRecord) [synthesized] — the proposed loan terms

**Outputs:**
- `verification` (VerificationResult) [synthesized] — the consolidated verification outcome
- `route_to_human` (bool) [synthesized] — whether digital closure must be blocked

### AGT-05 — Signature (SCA) Agent (BUILD)
Initiates PSD2 strong customer authentication through the mocked signature/SCA service, manages
retries and cancellation with clear messaging, and returns the signature result. It guarantees
that a loan cannot advance to the signed state without a successful SCA and blocks progression on
failure or cancellation.

**Inputs:**
- `document` (PrecontractualDocument) [synthesized] — the accepted precontractual document
- `verification` (VerificationResult) [synthesized] — the passed verification outcome

**Outputs:**
- `signature` (SignatureResult) [synthesized] — the SCA result
- `signed` (bool) [synthesized] — whether the loan may move to FIRMADO

### AGT-06 — Disbursement Agent (BUILD)
After a successful signature, creates the loan in the mocked core banking service and executes the
credit to the chosen account using an idempotency key so a repeated request never produces a
second credit. It generates the amortization schedule and prepares the confirmation, writing the
acceptance, signature, and disbursement events to the audit trail.

**Inputs:**
- `signature` (SignatureResult) [synthesized] — the successful signature
- `disbursement_account` (str) [synthesized] — the account to credit
- `idempotency_key` (str) [synthesized] — key guaranteeing a single credit

**Outputs:**
- `loan` (LoanRecord) [synthesized] — the created loan in its post-disbursement state
- `schedule` (AmortizationSchedule) [synthesized] — the generated amortization schedule

### AGT-07 — Journey Orchestrator (BUILD)
Sequences the agents across the loan lifecycle, holds the shared journey state so a customer can
save and resume (including across app and web), and enforces the ordering constraints between
steps — precontractual before signature, verifications before signature, signature before
disbursement. It stops the flow when the offer expires or is revoked before the signed state.

**Inputs:**
- `customer_id` (str) [synthesized] — the customer whose journey is orchestrated
- `journey_state` (LoanStatus) [synthesized] — the current lifecycle state

**Outputs:**
- `next_step` (str) [synthesized] — the next agent/step to invoke
- `journey_state` (LoanStatus) [synthesized] — the updated lifecycle state

# MCP Tool Contracts: Pre-Approved Loan Journey

<!-- Tool register synthesized from the integrations table; all I/O fields [synthesized]. -->

| Tool ID | Name | Used by | Status |
|---------|------|---------|--------|
| MCP-T01 | Offer Engine Reader | AGT-01 | MOCK |
| MCP-T02 | Pricing Calculator | AGT-02 | MOCK |
| MCP-T03 | Document Manager | AGT-03 | MOCK |
| MCP-T04 | Verification & Risk Register | AGT-04 | MOCK |
| MCP-T05 | Signature / SCA Service | AGT-05 | MOCK |
| MCP-T06 | Core Banking Disbursement | AGT-06 | MOCK |
| MCP-T07 | Account Lookup | AGT-06 | MOCK |
| MCP-T08 | Notification Sender | AGT-06 | MOCK |

## Tool specifications

### MCP-T01 — Offer Engine Reader (MOCK)
Reads a customer's live pre-approved offer from the mocked offer/scoring engine.

**Inputs:**
- `customer_id` (str) [synthesized] — the customer

**Outputs:**
- `offer` (Optional[PreApprovedOfferRecord]) [synthesized] — the live offer, if any

**Backend strategy:** MOCK — returns `PreApprovedOfferRecord` rows from a seed fixture keyed by
customer; the real offer/scoring API is deferred.

### MCP-T02 — Pricing Calculator (MOCK)
Computes payment and cost figures for a requested amount and term.

**Inputs:**
- `offer_id` (str) [synthesized] — the source offer
- `amount` (decimal) [synthesized] — requested amount
- `term_months` (int) [synthesized] — requested term

**Outputs:**
- `simulation` (SimulationRecord) [synthesized] — the computed simulation

**Backend strategy:** MOCK — a fixture pricing function returns deterministic figures; the real
pricing API is deferred.

### MCP-T03 — Document Manager (MOCK)
Produces and stores the INE/SECCI and contract, and records acceptance.

**Inputs:**
- `loan_id` (str) [synthesized] — the associated loan/simulation
- `accept` (bool) [synthesized] — whether the customer is accepting

**Outputs:**
- `document` (PrecontractualDocument) [synthesized] — the document with acceptance state

**Backend strategy:** MOCK — returns a fixture PDF reference and stamps an acceptance timestamp;
the real document management system is deferred.

### MCP-T04 — Verification & Risk Register (MOCK)
Runs solvency and antifraud/AML checks against the mocked risk register (CIRBE) and fraud services.

**Inputs:**
- `customer_id` (str) [synthesized] — the customer
- `amount` (decimal) [synthesized] — the proposed amount

**Outputs:**
- `verification` (VerificationResult) [synthesized] — the consolidated outcome

**Backend strategy:** MOCK — returns fixture outcomes (pass/fail per fixture customer); real CIRBE
and PBC/FT integrations are deferred.

### MCP-T05 — Signature / SCA Service (MOCK)
Performs PSD2 strong customer authentication and returns the result.

**Inputs:**
- `loan_id` (str) [synthesized] — the loan being signed
- `method` (str) [synthesized] — requested SCA method

**Outputs:**
- `signature` (SignatureResult) [synthesized] — the SCA result

**Backend strategy:** MOCK — returns a scripted success/failure per fixture; the real SCA provider
is deferred.

### MCP-T06 — Core Banking Disbursement (MOCK)
Creates the loan and credits the chosen account idempotently, returning the loan and schedule.

**Inputs:**
- `loan_id` (str) [synthesized] — the loan identifier
- `disbursement_account` (str) [synthesized] — the account to credit
- `idempotency_key` (str) [synthesized] — single-credit guarantee key

**Outputs:**
- `loan` (LoanRecord) [synthesized] — the created, disbursed loan
- `schedule` (AmortizationSchedule) [synthesized] — the amortization schedule

**Backend strategy:** MOCK — an in-memory core stub that records credits by `idempotency_key` and
returns the same result on repeat, so no double credit occurs; the real RSI core is deferred.

### MCP-T07 — Account Lookup (MOCK)
Lists the customer's accounts and whether each is active and operable.

**Inputs:**
- `customer_id` (str) [synthesized] — the customer

**Outputs:**
- `accounts` ([DisbursementAccountRecord]) [synthesized] — the customer's accounts

**Backend strategy:** MOCK — returns fixture account rows; the real core account API is deferred.

### MCP-T08 — Notification Sender (MOCK)
Sends the confirmation notification/email.

**Inputs:**
- `loan_id` (str) [synthesized] — the disbursed loan
- `channel` (str) [synthesized] — push or email

**Outputs:**
- `sent` (bool) [synthesized] — whether the notification was recorded

**Backend strategy:** MOCK — a no-op sink recording the payload; the real notification service is
deferred.

# Business Rules & Validation Logic: Pre-Approved Loan Journey

## Journey Business Rules (BR-01–BR-14)
The rule set the in-scope agents enforce across the journey. Enforced primarily by the
orchestrator (AGT-07) and the step agents named per rule.

| ID | Name | Inputs | Pass condition | Failure severity |
|----|------|--------|----------------|------------------|
| BR-01 | Live offer required | offer.status | equals OFERTA_VIGENTE | Hard block |
| BR-02 | Amount within offer | requested_amount, offer.max_amount, product_min | product_min ≤ amount ≤ offer.max_amount | Auto-correct and warn |
| BR-03 | Term within offer | requested_term_months, offer.max_term_months, product_min_term | product_min_term ≤ term ≤ offer.max_term_months | Auto-correct and warn |
| BR-04 | Recalc on change | requested_amount, requested_term_months | simulation figures recomputed on every change | Hard block |
| BR-05 | Rate with/without bonus | customer.has_relationship_bonus | both rates shown when a bonus applies | Soft warn |
| BR-06 | Precontractual before signature | document.accepted_at | non-null before signature | Hard block |
| BR-07 | SCA required | signature.succeeded | equals true before FIRMADO | Hard block |
| BR-08 | Disbursement after signature + verifications | signature.succeeded, verification.overall_passed | both true before credit | Hard block |
| BR-09 | Verification gate | verification.overall_passed | true to close digitally; else route to human | Route to HITL |
| BR-10 | Operable disbursement account | account.is_active, account.is_operable | both true | Hard block |
| BR-11 | Rights disclosure | withdrawal_shown, early_repayment_shown | both shown before signature | Hard block |
| BR-12 | Offer live during flow | offer.status | remains OFERTA_VIGENTE until FIRMADO | Hard block |
| BR-13 | Save and resume | offer.status | simulation resumable while offer live | Soft warn |
| BR-14 | Audit trail | acceptance, signature, disbursement events | all recorded immutably | Hard block |

## Field Validation Rules
Field-level checks applied on input.

| ID | Name | Inputs | Pass condition | Failure severity |
|----|------|--------|----------------|------------------|
| FV-01 | Amount numeric & bounded | requested_amount, product_min, offer.max_amount | numeric and within bounds | Hard block |
| FV-02 | Term integer & bounded | requested_term_months | integer within bounds, coherent with amount | Hard block |
| FV-03 | Account belongs to customer | disbursement_account, customer.account_ids | account is in the customer's set | Hard block |
| FV-04 | Documentation accepted | document.accepted_at | non-null before signature | Hard block |
| FV-05 | SCA attempts bounded | sca_attempt_count | ≤ 3 attempts [inferred — confirm with stakeholder] | Route to HITL |

**Product minimums:** minimum amount 1.000 € and minimum term 12 months [inferred — confirm with
stakeholder]; the SCA retry ceiling of 3 attempts is [inferred — confirm with stakeholder].

# UI Contracts: Pre-Approved Loan Journey

**Primary surface:** Web app (with mobile parity)

## Screens

### Offer discovery
Shows whether a live offer exists and its headline.
- **Data consumed:** `offer` (from AGT-01), `journey_available` (from AGT-01)
- **Actions:** start the simulation

### Offer detail
Shows the offer terms before configuring.
- **Data consumed:** `offer` (from AGT-01) — `max_amount`, `max_term_months`, `nominal_rate`, `valid_until`
- **Actions:** proceed to simulation

### Simulation
Lets the customer configure amount and term and see live figures.
- **Data consumed:** `simulation` (from AGT-02) — `monthly_payment`, `nominal_rate`, `effective_rate`, `total_cost`; `amount_clamped` (from AGT-02)
- **Actions:** adjust `requested_amount` and `requested_term_months`; save the simulation

### Summary & account selection
Confirms the configured loan and chooses the disbursement account.
- **Data consumed:** `simulation` (from AGT-02); `accounts` (from MCP-T07)
- **Actions:** select `disbursement_account`; confirm

### Precontractual information
Presents and captures acceptance of the INE/SECCI and contract.
- **Data consumed:** `document` (from AGT-03) — `document_url`, `accepted_at`
- **Actions:** read/download the document; accept

### Verification status
Shows verification progress transparently.
- **Data consumed:** `verification` (from AGT-04) — `overall_passed`; `route_to_human` (from AGT-04)
- **Actions:** continue when passed; contact an advisor when routed to human

### Signature (SCA)
Runs strong authentication.
- **Data consumed:** `signature` (from AGT-05) — `method`, `succeeded`
- **Actions:** authenticate; retry or cancel

### Confirmation
Confirms disbursement and gives access to documentation.
- **Data consumed:** `loan` (from AGT-06) — `loan_id`, `amount`, `disbursement_account`, `status`; `schedule` (from AGT-06)
- **Actions:** view the amortization schedule and documentation

## Reviewer surface (human hand-off)
When the verification gate routes to a human (BR-09), the customer sees the "cannot complete
online" message with an advisor/branch contact route; the routing decision and `verification`
outcome are written to the audit trail. There is no in-app reviewer approval in this iteration —
the human hand-off is out-of-band.
