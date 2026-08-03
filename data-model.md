# Data Model: Pre-Approved Loan Journey

## Entities

### EntityConfigurationRecord
The per-entity parameter set that particularizes the single common journey ("build once, deploy to
many"). Resolved before the journey is exposed; every downstream record carries its `entity_id`.
| Field | Type | Notes |
|-------|------|-------|
| `entity_id` | str | credit-union identifier within Grupo Caja Rural |
| `brand` | str | brand/theme key for UI theming |
| `locale` | str | active locale (e.g. `es-ES`; co-official languages per territory) |
| `product_min_amount` | decimal | catalog minimum amount for this entity |
| `product_max_amount` | decimal | catalog ceiling (an offer's `max_amount` may be lower) |
| `product_min_term_months` | int | catalog minimum term |
| `product_max_term_months` | int | catalog maximum term |
| `opening_fee_pct` | float | opening fee percentage for this entity |
| `relationship_bonus_pct` | float | rate bonus when the customer is bonus-eligible |
| `secci_template_id` | str | reference to the entity's SECCI/INE + contract template |
| `feature_flags` | dict | per-entity flags (e.g. channels enabled) |

### CustomerRecord
| Field | Type | Notes |
|-------|------|-------|
| `customer_id` | str | internal customer identifier |
| `entity_id` | str | owning entity (FK to EntityConfigurationRecord) |
| `segment` | str | customer segment |
| `has_relationship_bonus` | bool | whether a rate bonus applies |
| `account_ids` | [str] | the customer's account identifiers |

### PreApprovedOfferRecord
| Field | Type | Notes |
|-------|------|-------|
| `offer_id` | str | offer identifier |
| `customer_id` | str | owning customer |
| `entity_id` | str | owning entity (bounds catalog and legal texts) |
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
| `entity_id` | str | owning entity (segments the audit trail) |
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
`EN_SIMULACION | PENDIENTE_INFORMACION_PRECONTRACTUAL | PENDIENTE_VERIFICACIONES | PENDIENTE_FIRMA | FIRMADO | PENDIENTE_ABONO | ABONADO | ACTIVO | RECHAZADA_VERIFICACION | ABANDONADO`

> Post-contracting terminal states from the functional spec — `DESISTIDO` (14-day withdrawal) and
> `CANCELADO` (full early repayment) — belong to US3 and are **out of scope** for this MVP
> iteration; they are named here only so the enum stays forward-compatible.

Defined once here; referenced by name from spec.md, interfaces.md, and the state model below.

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

All external systems are mocked from seed fixtures for this iteration. At least two entity
configurations are seeded so parametrization is exercised without forking the flow. Shapes:

**Entity configuration** provides `EntityConfigurationRecord`. Example:
```json
{ "entity_id": "CR-SUR", "brand": "caja-rural-del-sur", "locale": "es-ES", "product_min_amount": 1000.00, "product_max_amount": 60000.00, "product_min_term_months": 12, "product_max_term_months": 96, "opening_fee_pct": 0.0, "relationship_bonus_pct": 0.5, "secci_template_id": "SECCI-CR-SUR-v1", "feature_flags": { "web": true, "app": true } }
```

**Offer/scoring engine** returns `PreApprovedOfferRecord`. Example:
```json
{ "offer_id": "OF-2001", "customer_id": "C-100", "entity_id": "CR-SUR", "max_amount": 20000.00, "max_term_months": 72, "nominal_rate": 6.5, "valid_until": "2026-12-31", "status": "OFERTA_VIGENTE" }
```

**Pricing engine** returns a `SimulationRecord`. Example:
```json
{ "offer_id": "OF-2001", "amount": 15000.00, "term_months": 60, "monthly_payment": 293.49, "nominal_rate": 6.5, "effective_rate": 6.98, "total_cost": 17609.40 }
```

**Core banking (RSI)** accepts a disbursement request keyed by `idempotency_key` and returns a
`LoanRecord` plus an `AmortizationSchedule`. Example loan record:
```json
{ "loan_id": "L-3001", "offer_id": "OF-2001", "entity_id": "CR-SUR", "amount": 15000.00, "term_months": 60, "nominal_rate": 6.5, "effective_rate": 6.98, "disbursement_account": "ES7620...", "status": "ABONADO", "disbursed_at": "2026-07-06T10:00:00Z", "idempotency_key": "OF-2001-15000-60" }
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
