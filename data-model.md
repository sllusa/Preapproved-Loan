# Data Model: Pre-Approved Loan Journey

## Entities

### CustomerRecord
| Field | Type | Notes |
|-------|------|-------|
| `customer_id` | str | internal customer identifier |
| `segment` | str | customer segment |
| `has_relationship_bonus` | bool | whether a rate bonus applies |
| `account_ids` | [str] | the customer's account identifiers |

### PreApprovedOfferRecord
| Field | Type | Notes |
|-------|------|-------|
| `offer_id` | str | offer identifier |
| `customer_id` | str | owning customer |
| `max_amount` | decimal | maximum pre-approved amount |
| `max_term_months` | int | maximum term in months |
| `nominal_rate` | float | applicable nominal interest rate (TIN) |
| `valid_until` | date | offer expiry date |
| `status` | OfferStatus | current offer status |

### SimulationRecord
| Field | Type | Notes |
|-------|------|-------|
| `offer_id` | str | source offer |
| `amount` | decimal | requested amount |
| `term_months` | int | requested term |
| `monthly_payment` | decimal | computed installment |
| `nominal_rate` | float | applied nominal rate (TIN) |
| `effective_rate` | float | effective annual rate (TAE) |
| `total_cost` | decimal | total cost of credit |

### LoanRecord
| Field | Type | Notes |
|-------|------|-------|
| `loan_id` | str | loan identifier |
| `offer_id` | str | originating offer |
| `amount` | decimal | contracted amount |
| `term_months` | int | contracted term |
| `nominal_rate` | float | nominal rate (TIN) |
| `effective_rate` | float | effective rate (TAE) |
| `disbursement_account` | str | account credited |
| `status` | LoanStatus | current lifecycle status |
| `disbursed_at` | Optional[datetime] | credit timestamp, once disbursed |
| `idempotency_key` | str | key guaranteeing single disbursement |

### AmortizationSchedule
| Field | Type | Notes |
|-------|------|-------|
| `loan_id` | str | owning loan |
| `installments` | [Installment] | ordered installments |

### Installment
| Field | Type | Notes |
|-------|------|-------|
| `number` | int | installment sequence number |
| `due_date` | date | payment date |
| `principal` | decimal | principal portion |
| `interest` | decimal | interest portion |
| `outstanding_principal` | decimal | remaining principal after this installment |

### PrecontractualDocument
| Field | Type | Notes |
|-------|------|-------|
| `document_id` | str | document identifier |
| `loan_id` | str | associated loan/simulation |
| `document_url` | str | link to the INE/SECCI + contract PDF |
| `accepted_at` | Optional[datetime] | acceptance evidence timestamp |

### VerificationResult
| Field | Type | Notes |
|-------|------|-------|
| `solvency_passed` | bool | light solvency evaluation outcome |
| `antifraud_passed` | bool | antifraud/AML (PBC/FT) outcome |
| `overall_passed` | bool | conjunction of the above |

### SignatureResult
| Field | Type | Notes |
|-------|------|-------|
| `method` | str | SCA method used (OTP / biometric / digital signature) |
| `succeeded` | bool | whether SCA succeeded |
| `signed_at` | Optional[datetime] | signature timestamp |

### DisbursementAccountRecord
| Field | Type | Notes |
|-------|------|-------|
| `iban` | str | account IBAN |
| `is_active` | bool | account is active |
| `is_operable` | bool | account can receive the credit |

## Enums (single source of truth)

### OfferStatus
`OFERTA_VIGENTE | CADUCADA | REVOCADA`

### LoanStatus
`EN_SIMULACION | PENDIENTE_INFORMACION_PRECONTRACTUAL | PENDIENTE_VERIFICACIONES | PENDIENTE_FIRMA | FIRMADO | ABONADO | ACTIVO | RECHAZADA_VERIFICACION | ABANDONADO | PENDIENTE_ABONO`

Defined once here; referenced by name from spec.md, contracts/interfaces.md, and the state model below.

## State models

### Loan lifecycle — required (the gate has more than one transition)
**States:**
- `EN_SIMULACION` — customer is configuring amount/term (initial state)
- `PENDIENTE_INFORMACION_PRECONTRACTUAL` — awaiting precontractual acceptance
- `PENDIENTE_VERIFICACIONES` — solvency/antifraud verifications running
- `PENDIENTE_FIRMA` — awaiting SCA signature
- `FIRMADO` — signed
- `PENDIENTE_ABONO` — disbursement requested, awaiting core confirmation
- `ABONADO` — funds credited, schedule generated
- `ACTIVO` — loan active post-disbursement
- `RECHAZADA_VERIFICACION` — verifications not passed (terminal for digital flow)
- `ABANDONADO` — abandoned through inactivity (terminal)

**Transitions:**
- `EN_SIMULACION → PENDIENTE_INFORMACION_PRECONTRACTUAL` — customer confirms simulation and account
- `PENDIENTE_INFORMACION_PRECONTRACTUAL → PENDIENTE_VERIFICACIONES` — customer accepts precontractual documentation
- `PENDIENTE_VERIFICACIONES → PENDIENTE_FIRMA` — verifications passed
- `PENDIENTE_VERIFICACIONES → RECHAZADA_VERIFICACION` — verifications not passed
- `PENDIENTE_FIRMA → FIRMADO` — SCA succeeds
- `FIRMADO → PENDIENTE_ABONO` — disbursement requested
- `PENDIENTE_ABONO → ABONADO` — core confirms the credit
- `ABONADO → ACTIVO` — schedule generated and loan activated
- `EN_SIMULACION → ABANDONADO` — inactivity timeout
- `PENDIENTE_INFORMACION_PRECONTRACTUAL → ABANDONADO` — inactivity timeout
- `PENDIENTE_FIRMA → ABANDONADO` — inactivity timeout

**Terminal states:** `ACTIVO`, `RECHAZADA_VERIFICACION`, `ABANDONADO`

> Offer expiry/revocation (`OFERTA_VIGENTE → CADUCADA | REVOCADA`) is modelled on the offer, not
> the loan; when it fires before `FIRMADO` the loan flow is stopped (see plan.md and research.md).

## Fixtures (MOCK external systems)

All external systems are mocked from seed fixtures for this iteration. Shapes:

**Offer/scoring engine** returns `PreApprovedOfferRecord`. Example:
```json
{ "offer_id": "OF-2001", "customer_id": "C-100", "max_amount": 20000.00, "max_term_months": 72, "nominal_rate": 6.5, "valid_until": "2026-12-31", "status": "OFERTA_VIGENTE" }
```

**Pricing engine** returns a `SimulationRecord`. Example:
```json
{ "offer_id": "OF-2001", "amount": 15000.00, "term_months": 60, "monthly_payment": 293.49, "nominal_rate": 6.5, "effective_rate": 6.98, "total_cost": 17609.40 }
```

**Core banking (RSI)** accepts a disbursement request keyed by `idempotency_key` and returns a
`LoanRecord` plus an `AmortizationSchedule`. Example loan record:
```json
{ "loan_id": "L-3001", "offer_id": "OF-2001", "amount": 15000.00, "term_months": 60, "nominal_rate": 6.5, "effective_rate": 6.98, "disbursement_account": "ES7620...", "status": "ABONADO", "disbursed_at": "2026-07-06T10:00:00Z", "idempotency_key": "OF-2001-15000-60" }
```

**Signature/SCA service** returns a `SignatureResult`. Example:
```json
{ "method": "OTP", "succeeded": true, "signed_at": "2026-07-06T09:58:00Z" }
```

**Antifraud/AML (PBC/FT) + CIRBE/solvency** return a `VerificationResult`. Example:
```json
{ "solvency_passed": true, "antifraud_passed": true, "overall_passed": true }
```

**Document manager** returns a `PrecontractualDocument`. Example:
```json
{ "document_id": "DOC-40", "loan_id": "L-3001", "document_url": "file://fixtures/ine_secci_40.pdf", "accepted_at": null }
```

**Accounts (from core)** return `DisbursementAccountRecord` rows. Example:
```json
{ "iban": "ES7620...", "is_active": true, "is_operable": true }
```

**Notifications** are mocked as no-op sinks recording the confirmation payload.
