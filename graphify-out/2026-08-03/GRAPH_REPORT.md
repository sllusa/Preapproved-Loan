# Graph Report - preapproved-loan  (2026-08-03)

## Corpus Check
- 141 files · ~50,361 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1494 nodes · 1849 edges · 121 communities (100 shown, 21 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 216 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `837b85b8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Agent specifications
- Core Principles
- Feature Specification: Pre-Approved Loan Journey — RSI / Ruralvía (Grupo Caja Rural)
- Entities
- Tasks: Pre-Approved Loan Journey
- Screens
- Tool specifications
- Implementation Plan: Pre-Approved Loan Journey
- Clarifications resolved
- Data Model: Pre-Approved Loan Journey
- Pre-Approved Loan Journey (Ruralvía) — Spec Kit Bundle
- Quickstart: Pre-Approved Loan Journey
- compilerOptions
- package.json
- main.py
- compilerOptions
- env.py
- amortization_installment.py
- amortization_schedule.py
- audit_event.py
- document_acknowledgement.py
- PreapprovedOfferSnapshot
- entity_configuration.py
- journey_instance.py
- acknowledge_documents
- signature_session.py
- simulation_snapshot.py
- verification_execution.py
- simulations.py
- __init__.py
- __init__.py
- preapproved-loan-backend
- check_journey_resume
- execute_booking
- list_offers
- JourneyInstance
- accounts.py
- PaginatedResponse
- database.py
- .execute_booking
- BookingService
- test_journey_router.py
- conftest.py
- config.py
- dependencies.py
- IdempotencyRecord
- ReconciliationCase
- StateTransitionError
- env.py
- DisbursementAccountSelection
- __init__.py
- test_iris_adapter.py
- test_pre_approval_adapter.py
- AmortizationAdapter
- SCAAdapter
- AccountAdapter
- DocumentAdapter
- test_verification_adapters.py
- AMLAdapter
- FraudAdapter
- SimulationSnapshot
- simulations.py
- DocumentAcknowledgement
- DocumentPackage
- scripts
- OutboxEvent
- .record_acknowledgement
- .generate_document_package
- .simulate
- package.json
- seed.py
- test_auth_module.py
- __init__.py
- test_fraud_screen_reject
- test_fraud_normalize_decision_by_score
- main.py
- list_offers
- eslint-plugin-react-hooks
- postcss
- tailwindcss
- @types/react-dom
- @typescript-eslint/eslint-plugin
- vite
- seed.py
- auth.py
- test_auth_router.py
- hash_password
- ServicingAdapter
- conftest.py
- IdempotencyRecord
- conftest.py
- Backend Development
- env.py
- 🚀 Quick Start
- Frontend Development
- start.sh
- OutboxEvent
- conftest.py
- 🏗️ Architecture
- 🛠️ Tech Stack
- ⚙️ Environment Variables
- ✅ Prerequisites
- vitest
- stop.sh
- ActivationService
- AmortizationSchedule
- LoanActivationProjection
- AmortizationInstallment
- test_fraud_screen_reject
- test_fraud_normalize_decision_by_score
- test_aml_screen_pass
- test_aml_screen_reject_sanctions

## God Nodes (most connected - your core abstractions)
1. `JourneyOrchestrator` - 28 edges
2. `ReconciliationWorker` - 23 edges
3. `SimulationService` - 20 edges
4. `compilerOptions` - 18 edges
5. `EntityConfiguration` - 16 edges
6. `ReconciliationCase` - 16 edges
7. `AuditService` - 16 edges
8. `BookingService` - 16 edges
9. `DocumentService` - 16 edges
10. `hash_password()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `ReconciliationWorker` --uses--> `IRISAdapter`  [INFERRED]
  backend/app/workers/reconciliation_worker.py → backend/app/adapters/iris_adapter.py
- `seed_users()` --calls--> `hash_password()`  [INFERRED]
  backend/app/seed.py → backend/app/auth.py
- `test_authenticate_user_with_inactive_account()` --calls--> `hash_password()`  [INFERRED]
  backend/tests/test_auth/test_auth_module.py → backend/app/auth.py
- `test_login_token_can_be_used_for_authentication()` --calls--> `hash_password()`  [INFERRED]
  backend/tests/test_auth/test_auth_router.py → backend/app/auth.py
- `test_login_with_invalid_password()` --calls--> `hash_password()`  [INFERRED]
  backend/tests/test_auth/test_auth_router.py → backend/app/auth.py

## Import Cycles
- None detected.

## Communities (121 total, 21 thin omitted)

### Community 0 - "Agent specifications"
Cohesion: 0.06
Nodes (34): Agent Contracts: Pre-Approved Loan Journey, Agent specifications, AGT-01 — Offer Discovery Agent (BUILD), AGT-02 — Simulation & Pricing Agent (BUILD), AGT-03 — Precontractual Agent (BUILD), AGT-04 — Verification Agent (BUILD), AGT-05 — Signature (SCA) Agent (BUILD), AGT-06 — Disbursement Agent (BUILD) (+26 more)

### Community 1 - "Core Principles"
Cohesion: 0.15
Nodes (12): Compliance & Hard Constraints, Core Principles, Governance, I. No Signature Without Precontractual Disclosure, II. Strong Customer Authentication Is Mandatory, III. Disbursement Is Idempotent and Gated, IV. Verifications Gate Digital Closure, Préstamo Preconcedido (Ruralvía) — Implementation Constitution (+4 more)

### Community 2 - "Feature Specification: Pre-Approved Loan Journey — RSI / Ruralvía (Grupo Caja Rural)"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: Pre-Approved Loan Journey — RSI / Ruralvía (Grupo Caja Rural), Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 3 - "Entities"
Cohesion: 0.10
Nodes (19): AmortizationSchedule, CustomerRecord, Data Model: Pre-Approved Loan Journey, DisbursementAccountRecord, Entities, EntityConfigurationRecord, Enums (single source of truth), Fixtures (MOCK external systems) (+11 more)

### Community 4 - "Tasks: Pre-Approved Loan Journey"
Cohesion: 0.17
Nodes (11): Component Conventions, Dependencies & Execution Order, Implementation Strategy, Parallel Example, Phase 1: Setup, Phase 2: Foundational (blocking), Phase 3: User Story 1 — Contract a pre-approved loan end to end (P1) 🎯 MVP, Phase 4: User Story 2 — Handle a customer who cannot close digitally (P2) (+3 more)

### Community 5 - "Screens"
Cohesion: 0.18
Nodes (9): lifespan(), Application lifespan events - startup and shutdown, Reconciliation Worker - Background polling for pending IRIS booking cases, Start the global reconciliation worker instance, Stop the global reconciliation worker instance, Start the reconciliation worker background task, Stop the reconciliation worker, start_reconciliation_worker() (+1 more)

### Community 6 - "Tool specifications"
Cohesion: 0.13
Nodes (15): autoprefixer, eslint, eslint-plugin-react-refresh, devDependencies, autoprefixer, eslint, eslint-plugin-react-refresh, @types/react (+7 more)

### Community 7 - "Implementation Plan: Pre-Approved Loan Journey"
Cohesion: 0.22
Nodes (8): Constitution Check, Documentation (this feature), Implementation Plan: Pre-Approved Loan Journey, Integration Strategy, Project Structure, Source Code, Summary, Technical Context

### Community 8 - "Clarifications resolved"
Cohesion: 0.22
Nodes (8): #1 — Behaviour when the offer expires or is revoked mid-flow, #2 — Handling a customer with multiple live offers, #3 — Multi-entity parametrization ("build once, deploy to many"), #4 — Legal baseline and CCD2 transition, Clarifications resolved, Phase 0 Research: Pre-Approved Loan Journey, Scope-boundary decisions, Tech-stack resolution

### Community 9 - "Data Model: Pre-Approved Loan Journey"
Cohesion: 0.17
Nodes (9): CreditworthinessAdapter, Any, Creditworthiness Verification Adapter - Light creditworthiness checks, Adapter for Creditworthiness Service integration.      Handles:     - Light cred, Normalize heterogeneous provider decisions to standard values.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform light creditworthiness verification.          Args:             customer, creditworthiness_adapter() (+1 more)

### Community 10 - "Pre-Approved Loan Journey (Ruralvía) — Spec Kit Bundle"
Cohesion: 0.29
Nodes (6): Attribution, Bundle contents & where the files go, Open decisions to revisit (see `research.md` and `spec.md` Assumptions), Pre-Approved Loan Journey (Ruralvía) — Spec Kit Bundle, What's next, What this is

### Community 11 - "Quickstart: Pre-Approved Loan Journey"
Cohesion: 0.50
Nodes (3): Acceptance gate (Definition of Done), How to verify (manual), Quickstart: Pre-Approved Loan Journey

### Community 12 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+16 more)

### Community 13 - "package.json"
Cohesion: 0.18
Nodes (11): clsx, dependencies, clsx, react, react-dom, react-router-dom, tailwind-merge, react (+3 more)

### Community 14 - "main.py"
Cohesion: 0.09
Nodes (22): AuditEvent, Base, Immutable audit event ledger for compliance evidence, Retrieve audit events for a customer, Retrieve audit events for a journey, db_session(), pending_reconciliation_case(), Tests for Reconciliation Worker (+14 more)

### Community 15 - "compilerOptions"
Cohesion: 0.22
Nodes (8): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include, vite.config.ts

### Community 16 - "env.py"
Cohesion: 0.15
Nodes (12): NotificationService, Any, Session, Notification Service - Customer messaging and notification orchestration, Notify customer that signature is required, Customer notification orchestration for journey milestones, status updates, and, Notify customer of successful disbursement, Notify customer that disbursement is being processed (+4 more)

### Community 17 - "amortization_installment.py"
Cohesion: 0.15
Nodes (16): activate_loan(), get_amortization_schedule(), get_loan_activation(), Session, Retrieve loan activation details., Activate loan and generate servicing handoff projection.      Creates loan activ, Retrieve complete amortization schedule for active loan.      Returns full repay, AmortizationInstallmentResponse (+8 more)

### Community 19 - "audit_event.py"
Cohesion: 0.14
Nodes (11): AuditService, Any, datetime, Session, Audit Service - Immutable audit event persistence, Search audit events with filters, Generate deterministic hash of payload, Captures immutable audit events for compliance evidence.     Implements append-o (+3 more)

### Community 21 - "document_acknowledgement.py"
Cohesion: 0.14
Nodes (16): DocumentService, Session, Document package generation (SECCI/INE), acknowledgement capture, evidence persi, db_session(), Tests for Document Service, Test document service falls back to supported language, Test recording document acknowledgement, Create an in-memory SQLite database for testing (+8 more)

### Community 22 - "PreapprovedOfferSnapshot"
Cohesion: 0.08
Nodes (24): PreapprovedOfferSnapshot, Base, Preapproved Offer Snapshot model, Retrieved offer evidence for journey start/resume, Tests for offers router, Test that list_offers validates entity configuration exists, Test GET /api/v1/offers/{offer_id} returns 404 for nonexistent offer, Test GET /api/v1/offers/{offer_id} returns offer details (+16 more)

### Community 23 - "entity_configuration.py"
Cohesion: 0.08
Nodes (22): EntityConfiguration, Base, Entity Configuration model, Multi-entity parameterization configuration, EntityConfigService, Any, Session, Entity Configuration Service - Multi-entity parameterization (+14 more)

### Community 24 - "journey_instance.py"
Cohesion: 0.10
Nodes (23): JourneyOrchestrator, Journey Orchestrator Service - Canonical state machine enforcement, Raised when an invalid state transition is attempted, Enforces lifecycle state machine with guarded transitions and audit event emissi, Validate that a state transition is allowed.          Args:             current_, Check if a state is terminal (no further transitions allowed), StateTransitionError, Tests for Journey Orchestrator Service (+15 more)

### Community 25 - "acknowledge_documents"
Cohesion: 0.17
Nodes (16): acknowledge_documents(), generate_document_package(), get_document_package(), Session, Retrieve a specific document package by ID., Generate legal document package (SECCI/INE) for the journey.      Resolves legal, Capture customer acknowledgement of document review.      Creates immutable audi, Config (+8 more)

### Community 26 - "signature_session.py"
Cohesion: 0.06
Nodes (32): Base, Signature Session model, SCA signature session tracking, SignatureSession, get_signature_session(), initiate_signature(), Session, Retrieve signature session status. (+24 more)

### Community 27 - "simulation_snapshot.py"
Cohesion: 0.12
Nodes (20): Simulation Service - Real-time pricing simulation, Stateless simulation API with amount/term validation and snapshot persistence., SimulationService, Tests for Simulation Service, Test simulation rejects termMonths > offer.maxTermMonths, Test simulation validates amount >= entity.minAmount, Test simulation calculates installment, total cost correctly, Test persisting simulation snapshot (+12 more)

### Community 28 - "verification_execution.py"
Cohesion: 0.06
Nodes (31): Base, Verification Execution model, Parallel checks execution header, VerificationExecution, Base, Verification Result model, Individual provider verification outcomes, VerificationResult (+23 more)

### Community 29 - "simulations.py"
Cohesion: 0.24
Nodes (9): Config, BaseModel, Schemas for simulation endpoints, Simulation calculation result, Confirm simulation and proceed to next step, Request to calculate simulation, SimulationConfirmRequest, SimulationRequest (+1 more)

### Community 34 - "check_journey_resume"
Cohesion: 0.06
Nodes (37): check_journey_resume(), get_journey(), Session, Journey orchestration and resume routes, Check if journey can be resumed and determine next step.      Validates offer st, Start a new journey for an offer.      Creates journey instance in OFERTA_VIGENT, Retrieve journey details., start_journey() (+29 more)

### Community 35 - "execute_booking"
Cohesion: 0.05
Nodes (37): IdempotencyRecord, Base, Idempotency Record model, Booking/disbursement command idempotency registry, execute_booking(), get_booking_status(), Session, Execute idempotent IRIS booking and disbursement.      Implements write-before-s (+29 more)

### Community 36 - "list_offers"
Cohesion: 0.05
Nodes (41): Acceptance Checks Verification, ✅ All MANDATORY infrastructure files created BEFORE TASK-8, ✅ api-client.ts attaches Authorization: Bearer {token} to all requests, ✅ api-client.ts base URL reads import.meta.env.VITE_API_URL or defaults to relative path, ✅ api-client.ts on 401 response: clears token, redirects to /login, API Contract Alignment, Application Entry Points, ✅ auth-context.tsx exports AuthProvider and useAuth() hook (+33 more)

### Community 37 - "JourneyInstance"
Cohesion: 0.24
Nodes (6): Any, JourneyInstance, Retrieve journey by ID, Apply state transition with guards and audit emission.          Args:, Update journey reference fields (simulation_id, account_id, etc.) without state, Create a new journey instance

### Community 38 - "accounts.py"
Cohesion: 0.13
Nodes (15): DisbursementAccountSelection, Base, Disbursement Account Selection model, Selected disbursement account with operability validation, list_disbursement_accounts(), Session, Retrieve eligible disbursement accounts for the customer.      Returns list of a, Select a disbursement account for the loan.      Validates account operability a (+7 more)

### Community 39 - "PaginatedResponse"
Cohesion: 0.17
Nodes (9): ErrorResponse, PaginatedResponse, BaseModel, Common schemas used across multiple endpoints, Pagination wrapper for list endpoints, Total number of pages, Whether there is a next page, Whether there is a previous page (+1 more)

### Community 40 - "database.py"
Cohesion: 0.17
Nodes (7): get_db(), Database connection and session management, Database session dependency for FastAPI routes, Audit Event model - immutable append-only ledger, Booking Command model, Reconciliation Case model, User model for authentication

### Community 41 - ".execute_booking"
Cohesion: 0.33
Nodes (4): Any, Simulate IRIS booking call (for testing), Get latest booking status for a journey, Execute idempotent booking command to IRIS.          Implements write-before-sen

### Community 42 - "BookingService"
Cohesion: 0.06
Nodes (31): AccountSelectRequest, AccountSelectResponse, AccountsResponse, ActivationStatusResponse, AmortizationInstallment, AmortizationScheduleResponse, AmortizationScheduleSummary, BookingExecuteResponse (+23 more)

### Community 43 - "test_journey_router.py"
Cohesion: 0.09
Nodes (22): Accessibility, Accessibility Testing, API Integration, API Integration Ready, Build Environment, Component Structure, Design Fidelity Implementation, Exact Color Matching (+14 more)

### Community 44 - "conftest.py"
Cohesion: 0.25
Nodes (8): calculate_simulation(), confirm_simulation(), get_simulation(), Session, Retrieve a specific simulation by ID., Calculate real-time simulation for requested amount and term.      Validates amo, Confirm simulation and proceed to account selection.      Advances journey state, SimulationRequest

### Community 45 - "config.py"
Cohesion: 0.12
Nodes (12): App(), LoginPage(), RequireAuth(), RequireAuthProps, AccountSelection(), ActiveLoanSummary(), AmortizationSchedule(), ChecksStatus() (+4 more)

### Community 46 - "dependencies.py"
Cohesion: 0.05
Nodes (37): 1. Default Credentials Consistency (5 Sources), 2. README Completeness and Accuracy, 3. Environment Configuration, 4. Startup Scripts, 5. Backend Functionality, 6. Cross-Layer API Contract Verification, Acceptance Criteria Status, API Base Path (+29 more)

### Community 48 - "ReconciliationCase"
Cohesion: 0.13
Nodes (21): BookingCommand, Base, IRIS booking command attempts and outcomes, Base, Pending timeout/uncertain IRIS booking resolution cases, ReconciliationCase, Session, Process a single reconciliation case.          Args:             db: Database se (+13 more)

### Community 49 - "StateTransitionError"
Cohesion: 0.18
Nodes (17): get_current_user(), User, Authentication dependency for protected routes.          Validates JWT token fro, Unit tests for auth dependencies - get_current_user, Test get_current_user raises 401 when user_id is not a valid integer, Test get_current_user returns User model with valid token, Test get_current_user raises 401 with invalid token, Test get_current_user raises 401 when user doesn't exist (+9 more)

### Community 50 - "env.py"
Cohesion: 0.24
Nodes (7): BottomNavigation(), Header(), HeaderProps, Layout(), LayoutProps, OfferLanding(), PreapprovedOffer

### Community 51 - "DisbursementAccountSelection"
Cohesion: 0.24
Nodes (12): Session, Idempotent seed data script, Seed sample journey instances - idempotent, Seed default admin user - idempotent, Execute seed data - idempotent operation.      Seeds:     - Default admin user (, Seed entity configurations - idempotent, Seed sample pre-approved offers - idempotent, run_seed() (+4 more)

### Community 55 - "test_iris_adapter.py"
Cohesion: 0.07
Nodes (23): IRISAdapter, Any, Adapter for IRIS Core and Disbursement API integration.      Handles:     - Idem, Poll booking status from IRIS.          Args:             iris_reference: IRIS l, Submit disbursement command for a booked loan.          Args:             iris_r, Initialize adapter with separate timeout budgets.          Args:             boo, Submit idempotent booking command to IRIS.          Args:             idempotenc, Initialize reconciliation worker.          Args:             poll_interval_secon (+15 more)

### Community 56 - "test_pre_approval_adapter.py"
Cohesion: 0.17
Nodes (12): Accounts, 📚 API Documentation, Authentication, Booking & Activation, Documents, Interactive API Docs, Journey, Key Endpoints (+4 more)

### Community 57 - "AmortizationAdapter"
Cohesion: 0.09
Nodes (20): AmortizationAdapter, Any, Adapter for Amortization Schedule Service integration.      Handles:     - Frenc, Retrieve existing amortization schedule.          Args:             loan_id: Loa, Normalize installment list for service layer.          Args:             raw_ins, Initialize adapter with timeout budget.          Args:             timeout: Requ, Generate French amortization schedule.          Args:             loan_id: Loan, adapter() (+12 more)

### Community 58 - "SCAAdapter"
Cohesion: 0.08
Nodes (21): Any, SCA Signature Adapter - PSD2/SCA strong customer authentication, Adapter for PSD2/SCA Signature Service integration.      Handles:     - Signatur, Verify signature session status.          Args:             session_id: Provider, Normalize provider callback status to standard values.          Args:, Initialize adapter with default timeout.          Args:             timeout: Req, Initiate SCA signature session.          Args:             customer_id: Customer, SCAAdapter (+13 more)

### Community 59 - "AccountAdapter"
Cohesion: 0.08
Nodes (21): AccountAdapter, Any, Account Validation Adapter - Disbursement account selection and operability, Adapter for Account Validation Service integration.      Handles:     - Eligible, Normalize account list response for service layer.          Args:             ra, Initialize adapter with timeout budget.          Args:             timeout: Requ, Retrieve eligible disbursement accounts for a customer.          Args:, Validate specific account operability for disbursement.          Args: (+13 more)

### Community 60 - "DocumentAdapter"
Cohesion: 0.08
Nodes (19): DocumentAdapter, Any, Document Generation Adapter - Legal package generation, Adapter for Document Generation Service integration.      Handles:     - SECCI/I, Get download URL for a generated document.          Args:             document_i, Normalize document list for service layer.          Args:             raw_docume, Initialize adapter with timeout budget.          Args:             timeout: Requ, Generate legal document package (SECCI or INE).          Args:             custo (+11 more)

### Community 61 - "test_verification_adapters.py"
Cohesion: 0.12
Nodes (15): Tests for Verification Adapters (Creditworthiness, Fraud, AML), Test fraud decision normalization by verdict, Test AML screening with PEP match (REVIEW), Test AML decision normalization, Test creditworthiness verification with PASS decision, Test creditworthiness verification with REJECT decision, Test decision normalization, Test fraud screening with PASS decision (+7 more)

### Community 63 - "FraudAdapter"
Cohesion: 0.17
Nodes (9): FraudAdapter, Any, Anti-Fraud Verification Adapter - Fraud screening, Adapter for Anti-Fraud Service integration.      Handles:     - Fraud risk scree, Normalize fraud screening result to standard decision.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform anti-fraud screening.          Args:             customer_id: Customer i, fraud_adapter() (+1 more)

### Community 64 - "SimulationSnapshot"
Cohesion: 0.15
Nodes (8): Base, Simulation Snapshot model, Confirmed and draft simulation versions, SimulationSnapshot, Persist simulation snapshot, Retrieve simulation snapshot by ID, Get latest simulation for a journey, Get confirmed simulation for a journey

### Community 65 - "simulations.py"
Cohesion: 0.12
Nodes (14): get_db(), Session, FastAPI dependencies for route handlers, Database session dependency, Disbursement account selection routes, Loan activation and amortization schedule routes, Authentication router - login endpoint, IRIS booking and disbursement routes (+6 more)

### Community 66 - "DocumentAcknowledgement"
Cohesion: 0.29
Nodes (5): DocumentAcknowledgement, Base, Document Acknowledgement model, Customer acknowledgement evidence for document packages, Retrieve document acknowledgement for a journey

### Community 67 - "DocumentPackage"
Cohesion: 0.29
Nodes (5): DocumentPackage, Base, Document Package model, Generated legal package metadata (SECCI/INE), Retrieve document package by ID

### Community 68 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test

### Community 69 - "OutboxEvent"
Cohesion: 0.22
Nodes (5): Amortization Schedule Adapter - Schedule generation and retrieval, IRIS Core and Disbursement Adapter - Booking and disbursement orchestration, Servicing Adapter - Active loan servicing handoff, Config, Application configuration management

### Community 70 - ".record_acknowledgement"
Cohesion: 0.40
Nodes (3): datetime, Document Service - Document generation and acknowledgement capture, Record customer acknowledgement of document package.          Captures immutable

### Community 71 - ".generate_document_package"
Cohesion: 0.33
Nodes (4): Any, Generate precontractual and contractual document package.          Resolves lega, Generate mock document metadata, DocumentPackage

### Community 72 - ".simulate"
Cohesion: 0.29
Nodes (4): Any, Session, Calculate loan pricing.         Simplified French amortization schedule calculat, Perform real-time simulation with validation.          Args:             journey

### Community 73 - "package.json"
Cohesion: 0.40
Nodes (4): description, name, type, version

### Community 74 - "seed.py"
Cohesion: 0.22
Nodes (9): Problem: Database Connection Error, Problem: Frontend Build Fails with TypeScript Errors, Problem: Frontend Cannot Reach Backend, Problem: JWT Token Expired / 401 Unauthorized, Problem: Migration Fails, Problem: Port Already in Use, Problem: Seed Script Fails, Problem: Virtual Environment Activation Fails (Windows) (+1 more)

### Community 75 - "test_auth_module.py"
Cohesion: 0.14
Nodes (14): create_access_token(), decode_access_token(), Generate JWT access token with customer_id, entity_id, and exp claims.      Args, Decode and validate JWT access token.      Args:         token: JWT token string, Test decoding expired JWT token returns None, Test JWT token includes customer_id, entity_id, user_id, and exp claims, Test JWT token expires after configured time, Test decoding valid JWT token returns payload (+6 more)

### Community 77 - "test_fraud_screen_reject"
Cohesion: 0.25
Nodes (7): 🤝 Contributing, 🔐 Default Credentials, 📝 License, 🎯 Overview, Ruralvía Pre-Approved Loan Platform, 📞 Support, 📋 Table of Contents

### Community 78 - "test_fraud_normalize_decision_by_score"
Cohesion: 0.07
Nodes (23): PreApprovalAdapter, Any, Pre-Approval Engine Adapter - Offer retrieval and eligibility, Adapter for Pre-Approval Engine integration.      Handles:     - Offer retrieval, Normalize offer response and apply entity-specific filtering.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Retrieve pre-approved offers for a customer.          Args:             customer, Revalidate offer status and check for revocation.          Args:             off (+15 more)

### Community 79 - "main.py"
Cohesion: 0.17
Nodes (9): AMLAdapter, Any, AML/PBC Verification Adapter - Anti-money laundering and PEP screening, Adapter for AML/PBC Service integration.      Handles:     - Anti-money launderi, Normalize AML/PBC screening result to standard decision.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform AML/PBC screening.          Args:             customer_id: Customer iden, aml_adapter() (+1 more)

### Community 88 - "seed.py"
Cohesion: 0.11
Nodes (17): JourneyInstance, Base, Journey Instance model - canonical process aggregate, Canonical journey state aggregate with lifecycle tracking, JourneyInstance, Check if customer has existing journey for this offer, Tests for journey router, Test GET /api/v1/journey/{journey_id} returns 404 (+9 more)

### Community 89 - "auth.py"
Cohesion: 0.24
Nodes (10): login(), LoginRequest, LoginResponse, BaseModel, Session, Login request payload, User information in response, Login response with access token and user info (+2 more)

### Community 90 - "test_auth_router.py"
Cohesion: 0.13
Nodes (16): Base, User model for authentication and authorization, User, Test user authentication fails for inactive account, test_authenticate_user_with_inactive_account(), Unit tests for auth router - login endpoint, Test that login token can be used to access protected routes, Test POST /api/v1/auth/login with valid credentials (+8 more)

### Community 91 - "hash_password"
Cohesion: 0.10
Nodes (28): authenticate_user(), get_user_by_id(), hash_password(), Session, User, Authentication module with JWT and bcrypt, Authenticate user by email and password.      Args:         db: Database session, Retrieve user by ID.      Args:         db: Database session         user_id: Us (+20 more)

### Community 95 - "ServicingAdapter"
Cohesion: 0.25
Nodes (6): Any, Adapter for Active-Loan Servicing Context integration.      Handles:     - Loan, Get active loan status from servicing context.          Args:             iris_r, Initialize adapter with timeout budget.          Args:             timeout: Requ, Project active loan to servicing context.          Args:             iris_refere, ServicingAdapter

### Community 96 - "conftest.py"
Cohesion: 0.22
Nodes (7): client(), mock_entity_config(), mock_user(), Pytest fixtures for router tests, Create test client with dependency overrides, Mock authenticated user, Create mock entity configuration

### Community 97 - "IdempotencyRecord"
Cohesion: 0.33
Nodes (5): health(), FastAPI application entry point, Root endpoint - health check, Health check endpoint, root()

### Community 98 - "conftest.py"
Cohesion: 0.40
Nodes (4): Parse CORS origins from comma-separated string, Application settings loaded from environment variables, Settings, BaseSettings

### Community 99 - "Backend Development"
Cohesion: 0.29
Nodes (7): Backend Development, Create Database Migration, 💻 Development, Manual Backend Startup (without frontend), Run Backend Linter, Run Backend Tests, Seed Database Manually

### Community 100 - "env.py"
Cohesion: 0.33
Nodes (5): Alembic migration environment configuration, Run migrations in 'offline' mode, Run migrations in 'online' mode, run_migrations_offline(), run_migrations_online()

### Community 102 - "🚀 Quick Start"
Cohesion: 0.33
Nodes (6): 1. Clone the Repository, 2. Start All Services (macOS/Linux), 3. Start All Services (Windows), 4. Access the Application, 5. Stop All Services, 🚀 Quick Start

### Community 103 - "Frontend Development"
Cohesion: 0.33
Nodes (6): Build for Production, Frontend Development, Manual Frontend Startup (without backend), Run Frontend Linter, Run Frontend Tests, Run Frontend Type Check

### Community 104 - "start.sh"
Cohesion: 0.47
Nodes (4): check_prerequisites(), DATABASE_URL, portable_sed(), start.sh script

### Community 105 - "OutboxEvent"
Cohesion: 0.40
Nodes (4): OutboxEvent, Base, Outbox Event model - transactional event publication, Transactional outbox for reliable event emission

### Community 106 - "conftest.py"
Cohesion: 0.50
Nodes (3): db_session(), Pytest fixtures for testing, Create an in-memory SQLite database session for testing.     Each test gets a fr

### Community 107 - "🏗️ Architecture"
Cohesion: 0.50
Nodes (4): 🏗️ Architecture, Data Flow, Page Components (Frontend), Service Modules (Backend)

### Community 108 - "🛠️ Tech Stack"
Cohesion: 0.50
Nodes (4): Backend, Frontend, Infrastructure, 🛠️ Tech Stack

### Community 109 - "⚙️ Environment Variables"
Cohesion: 0.50
Nodes (4): Backend Configuration (backend/.env), ⚙️ Environment Variables, Frontend Configuration (frontend/.env), Setup Example Files

### Community 110 - "✅ Prerequisites"
Cohesion: 0.50
Nodes (4): Optional, ✅ Prerequisites, Required, Verify Installation

### Community 113 - "ActivationService"
Cohesion: 0.22
Nodes (8): ActivationService, datetime, Session, Activation Service - Loan activation and amortization schedule retrieval, Generate amortization installments, Loan activation, amortization schedule retrieval, servicing handoff.     Integra, Create loan activation projection.          In production, waits for amortizatio, Generate amortization schedule.          In production, calls amortization sched

### Community 114 - "AmortizationSchedule"
Cohesion: 0.25
Nodes (6): AmortizationSchedule, Base, Amortization Schedule model, Loan repayment schedule header, Any, Get complete amortization schedule for a loan

### Community 115 - "LoanActivationProjection"
Cohesion: 0.29
Nodes (5): LoanActivationProjection, Base, Loan Activation Projection model, Loan activation and servicing readiness projection, Get loan activation projection for a journey

### Community 116 - "AmortizationInstallment"
Cohesion: 0.40
Nodes (4): AmortizationInstallment, Base, Amortization Installment model, Individual repayment installment details

## Knowledge Gaps
- **321 isolated node(s):** `Config`, `Config`, `Config`, `Config`, `Config` (+316 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JourneyOrchestrator` connect `journey_instance.py` to `check_journey_resume`, `JourneyInstance`, `accounts.py`, `conftest.py`, `ReconciliationCase`, `audit_event.py`, `acknowledge_documents`, `signature_session.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `IRISAdapter` connect `test_iris_adapter.py` to `ReconciliationCase`, `OutboxEvent`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `ReconciliationWorker` connect `ReconciliationCase` to `Screens`, `main.py`, `audit_event.py`, `test_iris_adapter.py`, `journey_instance.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `JourneyOrchestrator` (e.g. with `select_disbursement_account()` and `acknowledge_documents()`) actually correct?**
  _`JourneyOrchestrator` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ReconciliationWorker` (e.g. with `IRISAdapter` and `AuditService`) actually correct?**
  _`ReconciliationWorker` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `SimulationService` (e.g. with `calculate_simulation()` and `confirm_simulation()`) actually correct?**
  _`SimulationService` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `EntityConfiguration` (e.g. with `seed_entity_configurations()` and `.generate_document_package()`) actually correct?**
  _`EntityConfiguration` has 9 INFERRED edges - model-reasoned connections that need verification._